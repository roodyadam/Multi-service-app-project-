from flask import Flask, jsonify, request
import psycopg2
import redis
import os
import json

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ.get('POSTGRES_HOST', 'db'),
        database=os.environ.get('POSTGRES_DB', 'myapp'),
        user=os.environ.get('POSTGRES_USER', 'postgres'),
        password=os.environ.get('POSTGRES_PASSWORD', 'password')
    )
    return conn

redis_client = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'cache'),
    port=6379,
    decode_responses=True
)

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Database error: {e}")

@app.route('/')
def home():
    visits = redis_client.incr('page_visits')
    return f'''
        <h1>Multi-Container App: Flask + PostgreSQL + Redis</h1>
        <h2>Available Endpoints:</h2>
        <ul>
            <li><a href="/health">GET /health</a> - Health check</li>
            <li>POST /users - Create user</li>
            <li><a href="/users">GET /users</a> - List all users</li>
            <li>GET /users/id - Get user by ID</li>
            <li><a href="/cache-stats">GET /cache-stats</a> - Cache stats</li>
        </ul>
        <p>Page Visits: {visits} times</p>
    '''

@app.route('/health')
def health():
    try:
        conn = get_db_connection()
        conn.close()
        postgres_status = "connected"
    except:
        postgres_status = "disconnected"
    
    try:
        redis_client.ping()
        redis_status = "connected"
    except:
        redis_status = "disconnected"
    
    return jsonify({
        'status': 'healthy',
        'services': {
            'web': 'running',
            'postgres': postgres_status,
            'redis': redis_status
        }
    })

@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        
        if not name or not email:
            return jsonify({'error': 'Name and email required'}), 400
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id',
                (name, email)
            )
            user_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            
            redis_client.delete('all_users')
            
            return jsonify({
                'message': 'User created',
                'user_id': user_id,
                'name': name,
                'email': email
            }), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    else:
        cached = redis_client.get('all_users')
        
        if cached:
            return jsonify({
                'users': json.loads(cached),
                'source': 'Redis cache',
                'cache_hit': True
            })
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT id, name, email, created_at FROM users ORDER BY id')
            rows = cur.fetchall()
            cur.close()
            conn.close()
            
            users_list = [
                {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'created_at': str(row[3])
                }
                for row in rows
            ]
            
            redis_client.setex('all_users', 60, json.dumps(users_list))
            
            return jsonify({
                'users': users_list,
                'source': 'PostgreSQL database',
                'cache_hit': False
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/users/<int:user_id>')
def get_user(user_id):
    cache_key = f'user:{user_id}'
    cached = redis_client.get(cache_key)
    
    if cached:
        return jsonify({
            'user': json.loads(cached),
            'source': 'Redis cache',
            'cache_hit': True
        })
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, name, email, created_at FROM users WHERE id = %s', (user_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if not row:
            return jsonify({'error': 'User not found'}), 404
        
        user = {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'created_at': str(row[3])
        }
        
        redis_client.setex(cache_key, 300, json.dumps(user))
        
        return jsonify({
            'user': user,
            'source': 'PostgreSQL database',
            'cache_hit': False
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cache-stats')
def cache_stats():
    try:
        info = redis_client.info('stats')
        return jsonify({
            'total_connections': info.get('total_connections_received', 0),
            'total_commands': info.get('total_commands_processed', 0),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0),
            'cache_hit_ratio': round(
                info.get('keyspace_hits', 0) / 
                max(info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0), 1) * 100, 
                2
            )
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)