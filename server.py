from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import os
from datetime import datetime
from flask import session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Lưu trữ thông tin phòng và người dùng
rooms = {}
user_sessions = {}

# Hàm mã hóa AES
def encrypt_message_python(message, key):
    try:
        key = key.encode('utf-8')
        key = key[:32].ljust(32, b'\0')
        data = message.encode('utf-8')
        cipher = AES.new(key, AES.MODE_ECB)
        ct_bytes = cipher.encrypt(pad(data, AES.block_size))
        ct = base64.b64encode(ct_bytes).decode('utf-8')
        return ct
    except Exception as e:
        print(f"Encryption error: {e}")
        return None

# Hàm giải mã AES
def decrypt_message_python(encrypted_message, key):
    try:
        key = key.encode('utf-8')
        key = key[:32].ljust(32, b'\0')
        ct = base64.b64decode(encrypted_message)
        cipher = AES.new(key, AES.MODE_ECB)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        return None

@app.route('/encrypt', methods=['POST'])
def encrypt():
    data = request.json
    message = data.get('message')
    key = data.get('key')
    if not message or not key:
        return jsonify({'error': 'Missing message or key'}), 400
    encrypted = encrypt_message_python(message, key)
    if encrypted:
        return jsonify({'encrypted_message': encrypted})
    return jsonify({'error': 'Encryption failed'}), 500

@app.route('/decrypt', methods=['POST'])
def decrypt():
    data = request.json
    encrypted_message = data.get('encrypted_message')
    key = data.get('key')
    if not encrypted_message or not key:
        return jsonify({'error': 'Missing encrypted message or key'}), 400
    decrypted = decrypt_message_python(encrypted_message, key)
    if decrypted:
        return jsonify({'decrypted_message': decrypted})
    return jsonify({'error': 'Decryption failed'}), 500

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    session_id = request.sid
    print(f'Client disconnected: {session_id}')
    if session_id in user_sessions:
        user_info = user_sessions[session_id]
        room_id = user_info['room']
        username = user_info['username']
        if room_id in rooms and username in rooms[room_id]['users']:
            del rooms[room_id]['users'][username]
            emit('user_left', {
                'username': username,
                'room': room_id
            }, room=room_id)
            emit('user_list', {
                'room': room_id,
                'users': [
                    {
                        'username': u,
                        'avatar': info['avatar'],
                        'avatarType': info.get('avatarType', 'emoji'),
                        'avatarData': info.get('avatarData'),
                        'status': info.get('status', 'online')
                    }
                    for u, info in rooms[room_id]['users'].items()
                ]
            }, room=room_id)
            print(f"User {username} left room {room_id}")
            if not rooms[room_id]['users']:
                del rooms[room_id]
                print(f"Room {room_id} deleted (empty)")
        del user_sessions[session_id]

@socketio.on('join')
def handle_join(data):
    session_id = request.sid
    room_id = data['room']
    key = data['key']
    username = data['username']
    avatar = data.get('avatar', '😊')
    avatarType = data.get('avatarType', 'emoji')
    avatarData = data.get('avatarData')

    if room_id in rooms:
        if rooms[room_id]['key'] != key:
            emit('error', {'message': 'Invalid encryption key for this room'})
            return
        if username in rooms[room_id]['users']:
            emit('error', {'message': 'Username already taken in this room'})
            return
    else:
        rooms[room_id] = {
            'key': key,
            'users': {},
            'created_at': datetime.now()
        }
        print(f"Created new room: {room_id}")

    rooms[room_id]['users'][username] = {
        'avatar': avatar,
        'avatarType': avatarType,
        'avatarData': avatarData,
        'session_id': session_id,
        'joined_at': datetime.now(),
        'status': 'online',
        'last_activity': datetime.now()
    }

    user_sessions[session_id] = {
        'username': username,
        'room': room_id,
        'avatar': avatar,
        'avatarType': avatarType,
        'avatarData': avatarData,
        'status': 'online'
    }

    join_room(room_id)

    emit('user_joined', {
        'username': username,
        'avatar': avatar,
        'avatarType': avatarType,
        'avatarData': avatarData,
        'room': room_id
    }, room=room_id)

    emit('user_list', {
        'room': room_id,
        'users': [
            {
                'username': u,
                'avatar': info['avatar'],
                'avatarType': info.get('avatarType', 'emoji'),
                'avatarData': info.get('avatarData'),
                'status': info.get('status', 'online')
            }
            for u, info in rooms[room_id]['users'].items()
        ]
    }, room=room_id)

    print(f"User {username} joined room {room_id}")

@socketio.on('leave')
def handle_leave(data):
    session_id = request.sid
    room_id = data['room']
    username = data['username']

    leave_room(room_id)

    if room_id in rooms and username in rooms[room_id]['users']:
        del rooms[room_id]['users'][username]
        emit('user_left', {
            'username': username,
            'room': room_id
        }, room=room_id)
        emit('user_list', {
            'room': room_id,
            'users': [
                {
                    'username': u,
                    'avatar': info['avatar'],
                    'avatarType': info.get('avatarType', 'emoji'),
                    'avatarData': info.get('avatarData'),
                    'status': info.get('status', 'online')
                }
                for u, info in rooms[room_id]['users'].items()
            ]
        }, room=room_id)
        print(f"User {username} left room {room_id}")
        if not rooms[room_id]['users']:
            del rooms[room_id]
            print(f"Room {room_id} deleted (empty)")
    if session_id in user_sessions:
        del user_sessions[session_id]

@socketio.on('message')
def handle_message(data):
    session_id = request.sid
    room_id = data['room']
    encrypted_message = data['message']
    sender = data['sender']
    avatar = data.get('avatar', '😊')

    if room_id not in rooms or sender not in rooms[room_id]['users']:
        emit('error', {'message': 'You are not in this room'})
        return
    if session_id not in user_sessions:
        emit('error', {'message': 'Invalid session'})
        return

    emit('message', {
        'sender': sender,
        'message': encrypted_message,
        'avatar': avatar,
        'room': room_id,
        'timestamp': datetime.now().isoformat()
    }, room=room_id, include_self=False)

    print(f"Message from {sender} in room {room_id}")

@socketio.on('get_room_info')
def handle_get_room_info(data):
    room_id = data['room']
    if room_id in rooms:
        emit('room_info', {
            'room': room_id,
            'user_count': len(rooms[room_id]['users']),
            'users': [
                {
                    'username': u,
                    'avatar': info['avatar'],
                    'avatarType': info.get('avatarType', 'emoji'),
                    'avatarData': info.get('avatarData'),
                    'status': info.get('status', 'online'),
                    'joined_at': info.get('joined_at').isoformat() if info.get('joined_at') else None
                }
                for u, info in rooms[room_id]['users'].items()
            ]
        })
    else:
        emit('error', {'message': 'Room not found'})

@socketio.on('typing')
def handle_typing(data):
    session_id = request.sid
    room_id = data['room']
    username = data['username']
    is_typing = data['is_typing']
    if room_id in rooms and username in rooms[room_id]['users']:
        emit('user_typing', {
            'username': username,
            'is_typing': is_typing,
            'room': room_id
        }, room=room_id, include_self=False)

@socketio.on('private_message')
def handle_private_message(data):
    session_id = request.sid
    if session_id not in user_sessions:
        emit('error', {'message': 'Invalid session'})
        return
    
    sender_info = user_sessions[session_id]
    sender = sender_info['username']
    recipient = data['recipient']
    encrypted_message = data['message']
    room_id = sender_info['room']
    
    # Kiểm tra người nhận có trong phòng không
    if room_id not in rooms or recipient not in rooms[room_id]['users']:
        emit('error', {'message': 'Recipient not found in this room'})
        return
    
    # Gửi tin nhắn đến người nhận
    recipient_session_id = rooms[room_id]['users'][recipient]['session_id']
    
    emit('private_message', {
        'sender': sender,
        'recipient': recipient,
        'message': encrypted_message,
        'avatar': sender_info['avatar'],
        'avatarType': sender_info.get('avatarType', 'emoji'),
        'avatarData': sender_info.get('avatarData'),
        'timestamp': datetime.now().isoformat()
    }, room=recipient_session_id)
    
    # Gửi bản sao cho người gửi để hiển thị
    emit('private_message_sent', {
        'sender': sender,
        'recipient': recipient,
        'message': encrypted_message,
        'avatar': rooms[room_id]['users'][recipient]['avatar'],
        'avatarType': rooms[room_id]['users'][recipient].get('avatarType', 'emoji'),
        'avatarData': rooms[room_id]['users'][recipient].get('avatarData'),
        'timestamp': datetime.now().isoformat()
    }, room=session_id)
    
    print(f"Private message from {sender} to {recipient} in room {room_id}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/rooms')
def get_rooms():
    room_list = []
    for room_id, room_info in rooms.items():
        room_list.append({
            'id': room_id,
            'user_count': len(room_info['users']),
            'created_at': room_info['created_at'].isoformat()
        })
    return jsonify({'rooms': room_list})

@app.route('/api/room/<room_id>/users')
def get_room_users(room_id):
    if room_id in rooms:
        users = [
            {
                'username': username,
                'avatar': info['avatar'],
                'avatarType': info.get('avatarType', 'emoji'),
                'avatarData': info.get('avatarData'),
                'status': info.get('status', 'online'),
                'joined_at': info['joined_at'].isoformat()
            }
            for username, info in rooms[room_id]['users'].items()
        ]
        return jsonify({
            'room': room_id,
            'users': users,
            'total': len(users)
        })
    else:
        return jsonify({'error': 'Room not found'}), 404

if __name__ == '__main__':
    print("Starting Secure Chat Server...")
    print("Server will run on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)