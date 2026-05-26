import sqlite3
from flask import Flask, jsonify, request, session, render_template, send_from_directory

app = Flask(__name__)
app.secret_key = 'super-secret-key'

# [1] DB 초기화: B님의 규격에 맞춰 id(AUTOINCREMENT)와 address(주소) 추가
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 회원 테이블
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    cursor.execute('SELECT * FROM users WHERE username="admin"')
    if not cursor.fetchone():
        cursor.execute('INSERT INTO users VALUES ("admin", "1234")')
        
    # 주소록 테이블: id와 address 칼럼 추가!
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            address TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# [2] 화면 이동 라우트
@app.route('/')
def index():
    if 'user' not in session: 
        return render_template('auth/login.html')
    return render_template('search/index.html')

# 로그인 페이지로 직접 이동할 때를 위한 라우트 추가
@app.route('/login')
def login_page():
    return render_template('auth/login.html')

# [3] 정적 파일 서빙 라우트
@app.route('/templates/<path:filename>')
def custom_static(filename):
    return send_from_directory('templates', filename)

# [4] 인증 API: 로그인 (B님의 'id' 키 값에 맞춤)
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    # B님이 'id'로 보내므로 data.get('id')로 받아야 합니다.
    username = data.get('id')
    password = data.get('password')
    
    if username == 'admin' and password == '1234':
        session['user'] = 'admin'
        # B님의 auth.js가 alert(data.message)를 하므로 message도 채워줍니다.
        return jsonify({"success": True, "message": "로그인 성공!"})
    return jsonify({"success": False, "message": "아이디 또는 비밀번호가 틀렸습니다."}), 401

# [5] 인증 API: 로그아웃
@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    return jsonify({"success": True, "message": "로그아웃 되었습니다."})

# [6] 주소록 API: 조회 및 검색 (GET)
@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    # B님의 search.js 조건(403 분기)에 맞춰 인증 실패 시 403을 반환합니다.
    if 'user' not in session: 
        return jsonify([]), 403
        
    keyword = request.args.get('keyword', '')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # 이름, 전화번호, 주소 중 하나라도 걸리면 검색되도록 LIKE문 확장
    cursor.execute("""
        SELECT id, name, phone, address FROM contacts 
        WHERE name LIKE ? OR phone LIKE ? OR address LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
    rows = cursor.fetchall()
    conn.close()
    
    # B님이 사용하는 c.id, c.name, c.phone, c.address 딕셔너리 구조로 매핑
    return jsonify([
        {"id": r[0], "name": r[1], "phone": r[2], "address": r[3]} 
        for r in rows
    ])

# [7] 주소록 API: 추가 (POST)
@app.route('/api/contacts', methods=['POST'])
def add_contact():
    if 'user' not in session: 
        return jsonify({"success": False}), 403
        
    data = request.get_json()
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # B님이 보내는 name, phone, address 삼총사를 다 넣어줍니다.
    cursor.execute(
        "INSERT INTO contacts (name, phone, address) VALUES (?, ?, ?)", 
        (data.get('name'), data.get('phone'), data.get('address'))
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
