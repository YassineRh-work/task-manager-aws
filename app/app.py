#!/usr/bin/env python3
"""
Task Manager avec interface web complète
"""

from flask import Flask, request, jsonify, render_template_string
import os
import sqlite3
import boto3
from datetime import datetime
import json


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # Configuration base de données
    app.config['DB_PATH'] = 'taskmanager.db'

    # Configuration AWS
    try:
        s3_client = boto3.client('s3', region_name='eu-west-1')
        lambda_client = boto3.client('lambda', region_name='eu-west-1')
        aws_available = True
    except Exception:
        s3_client = None
        lambda_client = None
        aws_available = False

    # Initialiser SQLite
    def init_db():
        conn = sqlite3.connect(app.config['DB_PATH'])
        conn.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT 0,
                priority TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Données de démonstration
        existing = conn.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
        if existing == 0:
            demo_tasks = [
                ('Deployer infrastructure AWS',
                 'Utiliser CloudFormation pour creer EC2, S3, Lambda',
                 'high', 1),
                ('Configurer CI/CD Pipeline',
                 'Mettre en place CodePipeline pour deploiement automatique',
                 'high', 0),
                ('Implementer monitoring',
                 'Configurer CloudWatch pour surveiller les metriques',
                 'medium', 0),
                ('Tests de charge',
                 'Valider les performances de l\'application',
                 'medium', 0),
                ('Documentation technique',
                 'Rediger la documentation pour l\'equipe',
                 'low', 0),
                ('Optimisation couts',
                 'Analyser et optimiser l\'utilisation AWS',
                 'low', 0)
            ]

            for title, desc, priority, completed in demo_tasks:
                conn.execute(
                    ('INSERT INTO tasks (title, description, priority, '
                     'completed) VALUES (?, ?, ?, ?)'),
                    (title, desc, priority, completed)
                )

        conn.commit()
        conn.close()

    init_db()

    # Template HTML pour l'interface
    HTML_TEMPLATE = '''
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Task Manager - AWS Cloud Application</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }

            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }

            .header {
                background: linear-gradient(135deg, #ff6b6b, #ffa726);
                color: white;
                padding: 30px;
                text-align: center;
            }

            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }

            .header p {
                font-size: 1.2em;
                opacity: 0.9;
            }

            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                padding: 30px;
                background: #f8f9fa;
            }

            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                border-left: 4px solid;
            }

            .stat-card.total { border-left-color: #3498db; }
            .stat-card.completed { border-left-color: #2ecc71; }
            .stat-card.pending { border-left-color: #f39c12; }
            .stat-card.high { border-left-color: #e74c3c; }

            .stat-number {
                font-size: 2em;
                font-weight: bold;
                margin-bottom: 5px;
            }

            .stat-label {
                color: #666;
                font-size: 0.9em;
            }

            .main-content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 30px;
                padding: 30px;
            }

            .task-form {
                background: #f8f9fa;
                padding: 25px;
                border-radius: 15px;
                border: 2px dashed #ddd;
            }

            .task-form h3 {
                margin-bottom: 20px;
                color: #333;
                font-size: 1.3em;
            }

            .form-group {
                margin-bottom: 15px;
            }

            .form-group label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #555;
            }

            .form-group input,
            .form-group textarea,
            .form-group select {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 1em;
                transition: border-color 0.3s;
            }

            .form-group input:focus,
            .form-group textarea:focus,
            .form-group select:focus {
                outline: none;
                border-color: #667eea;
            }

            .btn {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 12px 25px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1em;
                font-weight: bold;
                transition: transform 0.2s;
                width: 100%;
            }

            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }

            .task-list {
                background: white;
            }

            .task-list h3 {
                margin-bottom: 20px;
                color: #333;
                font-size: 1.3em;
                border-bottom: 2px solid #eee;
                padding-bottom: 10px;
            }

            .task-item {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 15px;
                transition: transform 0.2s, box-shadow 0.2s;
                border-left: 4px solid;
            }

            .task-item:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }

            .task-item.high { border-left-color: #e74c3c; }
            .task-item.medium { border-left-color: #f39c12; }
            .task-item.low { border-left-color: #2ecc71; }
            .task-item.completed { opacity: 0.7; background: #f9f9f9; }

            .task-title {
                font-weight: bold;
                margin-bottom: 8px;
                font-size: 1.1em;
            }

            .task-description {
                color: #666;
                margin-bottom: 10px;
                line-height: 1.4;
            }

            .task-meta {
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 0.9em;
                color: #888;
            }

            .priority-badge {
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8em;
                font-weight: bold;
            }

            .priority-high { background: #ffe6e6; color: #d63031; }
            .priority-medium { background: #fff4e6; color: #e17055; }
            .priority-low { background: #e6ffe6; color: #00b894; }

            .aws-info {
                grid-column: 1 / -1;
                background: linear-gradient(135deg, #74b9ff, #0984e3);
                color: white;
                padding: 25px;
                border-radius: 15px;
                margin-top: 20px;
            }

            .aws-services {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }

            .service-item {
                text-align: center;
                padding: 15px;
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                backdrop-filter: blur(10px);
            }

            .service-item i {
                font-size: 2em;
                margin-bottom: 8px;
                display: block;
            }

            .toggle-btn {
                background: none;
                border: 2px solid #ddd;
                padding: 5px 10px;
                border-radius: 5px;
                cursor: pointer;
                transition: all 0.3s;
            }

            .toggle-btn:hover {
                background: #007bff;
                color: white;
                border-color: #007bff;
            }

            @media (max-width: 768px) {
                .main-content {
                    grid-template-columns: 1fr;
                }

                .stats {
                    grid-template-columns: repeat(2, 1fr);
                }

                .header h1 {
                    font-size: 1.8em;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 Task Manager</h1>
                <p>Application Multi-Tier deployee sur AWS Cloud</p>
            </div>

            <div class="stats">
                <div class="stat-card total">
                    <div class="stat-number">{{ stats.total }}</div>
                    <div class="stat-label">Total taches</div>
                </div>
                <div class="stat-card completed">
                    <div class="stat-number">{{ stats.completed }}</div>
                    <div class="stat-label">Terminees</div>
                </div>
                <div class="stat-card pending">
                    <div class="stat-number">{{ stats.pending }}</div>
                    <div class="stat-label">En cours</div>
                </div>
                <div class="stat-card high">
                    <div class="stat-number">{{ stats.high_priority }}</div>
                    <div class="stat-label">Priorite haute</div>
                </div>
            </div>

            <div class="main-content">
                <div class="task-form">
                    <h3>➕ Nouvelle tache</h3>
                    <form id="taskForm">
                        <div class="form-group">
                            <label for="title">Titre *</label>
                            <input type="text" id="title" name="title" required
                                   placeholder="Ex: Configurer monitoring CloudWatch">
                        </div>

                        <div class="form-group">
                            <label for="description">Description</label>
                            <textarea id="description" name="description" rows="3"
                                      placeholder="Details de la tache..."></textarea>
                        </div>

                        <div class="form-group">
                            <label for="priority">Priorite</label>
                            <select id="priority" name="priority">
                                <option value="low">🟢 Basse</option>
                                <option value="medium" selected>🟡 Moyenne</option>
                                <option value="high">🔴 Haute</option>
                            </select>
                        </div>

                        <button type="submit" class="btn">Creer la tache</button>
                    </form>
                </div>

                <div class="task-list">
                    <h3>📋 Liste des taches</h3>
                    <div id="taskContainer">
                        {% for task in tasks %}
                        <div class="task-item {{ task.priority }} {% if task.completed %}completed{% endif %}" data-id="{{ task.id }}">
                            <div class="task-title">{{ task.title }}</div>
                            <div class="task-description">{{ task.description or 'Aucune description' }}</div>
                            <div class="task-meta">
                                <span class="priority-badge priority-{{ task.priority }}">{{ task.priority.upper() }}</span>
                                <button class="toggle-btn" onclick="toggleTask({{ task.id }}, {{ task.completed }})">
                                    {% if task.completed %}❌ Annuler{% else %}✅ Terminer{% endif %}
                                </button>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>

                <div class="aws-info">
                    <h3>☁️ Architecture AWS deployee</h3>
                    <p><strong>Cout mensuel:</strong> 0€ (Free Tier) • <strong>Region:</strong> eu-west-1 • <strong>Statut:</strong> ✅ Operationnel</p>

                    <div class="aws-services">
                        <div class="service-item">
                            <i>🖥️</i>
                            <div>EC2 t3.micro</div>
                            <small>750h/mois gratuit</small>
                        </div>
                        <div class="service-item">
                            <i>🗂️</i>
                            <div>S3 Bucket</div>
                            <small>5GB gratuit</small>
                        </div>
                        <div class="service-item">
                            <i>⚡</i>
                            <div>Lambda</div>
                            <small>1M requetes/mois</small>
                        </div>
                        <div class="service-item">
                            <i>🏗️</i>
                            <div>CloudFormation</div>
                            <small>Infrastructure as Code</small>
                        </div>
                        <div class="service-item">
                            <i>🔐</i>
                            <div>IAM & VPC</div>
                            <small>Securite integree</small>
                        </div>
                        <div class="service-item">
                            <i>📊</i>
                            <div>CloudWatch</div>
                            <small>Monitoring</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Soumission du formulaire
            document.getElementById('taskForm').addEventListener('submit', async function(e) {
                e.preventDefault();

                const formData = new FormData(e.target);
                const data = Object.fromEntries(formData);

                try {
                    const response = await fetch('/api/tasks', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });

                    if (response.ok) {
                        location.reload();
                    } else {
                        alert('Erreur lors de la creation de la tache');
                    }
                } catch (error) {
                    alert('Erreur de connexion');
                }
            });

            // Basculer le statut d'une tache
            async function toggleTask(taskId, currentStatus) {
                try {
                    const response = await fetch(`/api/tasks/${taskId}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({completed: !currentStatus})
                    });

                    if (response.ok) {
                        location.reload();
                    }
                } catch (error) {
                    alert('Erreur lors de la mise a jour');
                }
            }

            // Mettre a jour l'horloge
            function updateTime() {
                const now = new Date();
                document.title = `Task Manager (${now.toLocaleTimeString()})`;
            }
            setInterval(updateTime, 1000);
        </script>
    </body>
    </html>
    '''

    # Routes
    @app.route('/')
    def index():
        # Récupérer les tâches
        conn = sqlite3.connect(app.config['DB_PATH'])
        conn.row_factory = sqlite3.Row

        tasks = conn.execute(
            'SELECT * FROM tasks ORDER BY created_at DESC'
        ).fetchall()
        tasks = [dict(task) for task in tasks]

        # Calculer les statistiques
        stats = {
            'total': len(tasks),
            'completed': len([t for t in tasks if t['completed']]),
            'pending': len([t for t in tasks if not t['completed']]),
            'high_priority': len([
                t for t in tasks
                if t['priority'] == 'high' and not t['completed']
            ])
        }

        conn.close()

        return render_template_string(HTML_TEMPLATE, tasks=tasks, stats=stats)

    @app.route('/health')
    def health():
        return jsonify({
            'status': 'healthy',
            'app': 'Task Manager avec interface web',
            'aws_available': aws_available
        })

    @app.route('/api/tasks', methods=['GET'])
    def get_tasks():
        conn = sqlite3.connect(app.config['DB_PATH'])
        conn.row_factory = sqlite3.Row
        tasks = conn.execute(
            'SELECT * FROM tasks ORDER BY created_at DESC'
        ).fetchall()
        conn.close()
        return jsonify([dict(task) for task in tasks])

    @app.route('/api/tasks', methods=['POST'])
    def create_task():
        data = request.get_json()

        if not data.get('title'):
            return jsonify({'error': 'Title required'}), 400

        conn = sqlite3.connect(app.config['DB_PATH'])
        cursor = conn.execute(
            'INSERT INTO tasks (title, description, priority) VALUES (?, ?, ?)',
            (data['title'], data.get('description', ''),
             data.get('priority', 'medium'))
        )
        task_id = cursor.lastrowid
        conn.commit()

        # Récupérer la tâche créée
        task = conn.execute(
            'SELECT * FROM tasks WHERE id = ?', (task_id,)
        ).fetchone()
        conn.close()

        # Déclencher Lambda si disponible
        if lambda_client:
            try:
                lambda_client.invoke(
                    FunctionName='final-working-notifications',
                    InvocationType='Event',
                    Payload=json.dumps({
                        'task_id': task_id,
                        'action': 'created',
                        'title': data['title']
                    })
                )
            except Exception:
                pass

        return jsonify(dict(task)), 201

    @app.route('/api/tasks/<int:task_id>', methods=['PUT'])
    def update_task(task_id):
        data = request.get_json()

        conn = sqlite3.connect(app.config['DB_PATH'])

        # Construire la requête de mise à jour
        updates = []
        params = []

        if 'title' in data:
            updates.append('title = ?')
            params.append(data['title'])
        if 'description' in data:
            updates.append('description = ?')
            params.append(data['description'])
        if 'completed' in data:
            updates.append('completed = ?')
            params.append(data['completed'])
        if 'priority' in data:
            updates.append('priority = ?')
            params.append(data['priority'])

        updates.append('updated_at = CURRENT_TIMESTAMP')
        params.append(task_id)

        query = f'UPDATE tasks SET {", ".join(updates)} WHERE id = ?'
        conn.execute(query, params)
        conn.commit()

        # Récupérer la tâche mise à jour
        task = conn.execute(
            'SELECT * FROM tasks WHERE id = ?', (task_id,)
        ).fetchone()
        conn.close()

        return jsonify(dict(task) if task else {'error': 'Task not found'})

    @app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
    def delete_task(task_id):
        conn = sqlite3.connect(app.config['DB_PATH'])
        conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()

        return jsonify({'deleted': True})

    # Tests AWS
    @app.route('/test-lambda')
    def test_lambda():
        if not lambda_client:
            return jsonify({'error': 'Lambda not available'})

        try:
            response = lambda_client.invoke(
                FunctionName='final-working-notifications',
                InvocationType='RequestResponse',
                Payload=json.dumps({'test': 'interface web'})
            )
            result = json.loads(response['Payload'].read())
            return jsonify({'lambda_test': 'SUCCESS', 'response': result})
        except Exception as e:
            return jsonify({'lambda_test': 'ERROR', 'error': str(e)})

    @app.route('/test-s3')
    def test_s3():
        if not s3_client:
            return jsonify({'error': 'S3 not available'})

        try:
            bucket_name = os.environ.get(
                'S3_BUCKET', 'final-working-221904544400-eu-west-1'
            )
            s3_client.put_object(
                Bucket=bucket_name,
                Key='interface-test.txt',
                Body=f'Test depuis interface web - {datetime.now().isoformat()}'
            )
            return jsonify({'s3_test': 'SUCCESS', 'bucket': bucket_name})
        except Exception as e:
            return jsonify({'s3_test': 'ERROR', 'error': str(e)})

    return app


if __name__ == '__main__':
    app = create_app()
    print("🚀 Task Manager avec interface web")
    print("📱 Interface: http://localhost:5000/")
    print("🔌 API: http://localhost:5000/api/tasks")
    app.run(host='0.0.0.0', port=5000, debug=True)
    