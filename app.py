import sqlite3
from flask import Flask, jsonify, request, session, render_template, send_from_directory

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # 세션 암호화용 키

# [1] DB 초기화: 파일이 없으면 만들고, 테이블과 테스트 계정까지 자동 세팅
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 회원 테이블 생성 및 admin 계정 추가
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    cursor.execute('SELECT * FROM users WHERE username="admin"')
    if not cursor.fetchone():
        cursor.execute('INSERT INTO users VALUES ("admin", "1234")')
        
    # 주소록 테이블 생성
    cursor.execute('CREATE TABLE IF NOT EXISTS contacts (name TEXT, phone TEXT)')
    conn.commit()
    conn.close()

init_db()

# [2] 화면 이동(렌더링) 라우트
@app.route('/')
def index():
    # 세션에 로그인 정보가 없으면 무조건 로그인 화면으로 튕겨냄 (과제 조건)
    if 'user' not in session: 
        return render_template('auth/login.html')
    return render_template('search/index.html')

# [3] 과제 규칙(auth, search 폴더 내 .js 파일 호출)을 위한 정적 파일 라우트
@app.route('/templates/<path:filename>')
def custom_static(filename):
    return send_from_directory('templates', filename)

# [4] 인증 API: 로그인
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    if data.get('username') == 'admin' and data.get('password') == '1234':
        session['user'] = 'admin'  # 세션 생성
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "아이디 또는 비밀번호가 틀렸습니다."}), 401

# [5] 인증 API: 로그아웃
@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)  # 세션 제거
    return jsonify({"success": True})

# [6] 주소록 API: 조회 및 검색 (GET)
@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    if 'user' not in session: 
        return jsonify([]), 401
        
    keyword = request.args.get('keyword', '')  # 검색어 가져오기
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # LIKE 구문으로 검색어 필터링 (검색어가 비어있으면 전체 조회됨)
    cursor.execute("SELECT name, phone FROM contacts WHERE name LIKE ?", (f"%{keyword}%",))
    rows = cursor.fetchall()
    conn.close()
    
    # 프론트엔드가 자바스크립트 배열로 다루기 쉽게 변환하여 반환
    return jsonify([{"name": r[0], "phone": r[1]} for r in rows])

# [7] 주소록 API: 추가 (POST)
@app.route('/api/contacts', methods=['POST'])
def add_contact():
    if 'user' not in session: 
        return jsonify({"success": False}), 401
        
    data = request.get_json()
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO contacts VALUES (?, ?)", (data['name'], data['phone']))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
