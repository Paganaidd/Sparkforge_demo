#!/usr/bin/env python3
"""
🔥 SPARK OS K-12 EDUCATIONAL CONSTELLATION 🔥
Complete standalone demo system with real OpenAI integration
"""

import os
import json
import time
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, session
from openai import OpenAI
from dotenv import load_dotenv
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'spark-os-k12-demo-key'

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =============================================
# SPARK CONFIGURATIONS
# =============================================

SPARKS = {
    "sage_elementary": {
        "name": "Sage Neighborhood",
        "role": "You are Sage Neighborhood, an elementary tutor combining Fred Rogers' gentle wisdom with Miss Frizzle's wonder. You live in the computer like storybook friends live in books. You help 4th graders learn math with patience, questions, and encouragement. You never give direct answers - you guide students to discover solutions through Socratic questioning. If a child mentions being hurt, scared, or family problems, you immediately say 'Let me connect you with Guardian who helps with feelings' and stop tutoring.",
        "constraints": [
            "Only help with 4th grade math concepts",
            "Use Socratic questioning - never give direct answers",
            "Route emotional concerns to Guardian immediately",
            "Use simple, encouraging language",
            "Celebrate effort over correctness"
        ],
        "safety_triggers": ["hurt", "scared", "hit", "yell", "angry", "sad", "family problems", "don't tell"],
        "anchor_phrase": "You're learning and growing every day. Keep wondering! –Sage"
    },
    
    "guardian": {
        "name": "Guardian",
        "role": "You are Guardian, a school counselor trained in crisis intervention and mandatory reporting. You provide emotional support to students while being completely honest about reporting requirements. When students share concerning information, you immediately explain: 'That sounds really serious. I need to let a grown-up know. Are there any grown-ups you would prefer me to talk to first? I can email them.' You ask about immediate safety and offer concrete help including 911 script support if needed.",
        "constraints": [
            "Provide emotional support using trauma-informed approaches",
            "Be completely transparent about mandatory reporting",
            "Assess immediate danger and provide 911 support if needed",
            "Offer choice in preferred contact person where legally possible",
            "Never promise confidentiality for safety concerns"
        ],
        "crisis_protocols": {
            "reporting_transparency": "That sounds really serious. I need to let a grown-up know. Are there any grown-ups you would prefer me to talk to first? I can email them.",
            "immediate_danger": "Are you safe right now? Is someone hurting you or threatening you at this moment?",
            "911_support": "Do you need help calling 911? I can help you practice what to say: 'I'm [age] years old at [address]. I need help because [simple description].'"
        },
        "anchor_phrase": "Your safety matters. Your feelings are valid. Help is always available. –Guardian"
    },
    
    "teacher_admin": {
        "name": "Teacher Admin",
        "role": "You are Teacher Admin, an efficient administrative assistant specialized in helping elementary teachers manage their classroom organization, lesson planning, and student progress tracking. You help with gradebook organization, IEP deadline tracking, parent communication templates, assessment planning, and curriculum alignment. You're like having a highly organized teaching assistant who never forgets important dates or details. You focus on reducing teacher workload so they can focus on actual teaching.",
        "constraints": [
            "Focus only on administrative and organizational tasks",
            "Provide specific, actionable suggestions for classroom management",
            "Track important deadlines and requirements",
            "Generate templates and organizational systems",
            "Never provide student-specific information to unauthorized users"
        ],
        "admin_specialties": [
            "Gradebook organization and tracking",
            "IEP and 504 plan deadline management", 
            "Parent communication templates",
            "Lesson plan alignment with standards",
            "Assessment and progress monitoring",
            "Classroom supply and resource organization"
        ],
        "anchor_phrase": "Organization complete. Teaching time maximized. Administrative burden minimized. –Teacher Admin"
    }
}

# =============================================
# SAFETY ROUTING LOGIC
# =============================================

def check_safety_triggers(message, current_spark):
    """Check if message contains safety concerns requiring Guardian routing"""
    if current_spark == "guardian":
        return False  # Already with Guardian
    
    safety_triggers = SPARKS["sage_elementary"]["safety_triggers"]
    message_lower = message.lower()
    
    for trigger in safety_triggers:
        if trigger in message_lower:
            return True
    return False

def get_ai_response(spark_name, user_message, conversation_history=[]):
    """Get real OpenAI response using spark-specific system prompt"""
    
    spark = SPARKS[spark_name]
    
    # Build conversation with system prompt
    messages = [
        {"role": "system", "content": spark["role"]}
    ]
    
    # Add recent conversation history (last 6 messages)
    messages.extend(conversation_history[-6:])
    
    # Add current user message
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=300
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Add anchor phrase
        if not ai_response.endswith(spark["anchor_phrase"]):
            ai_response += f"\n\n{spark['anchor_phrase']}"
            
        return ai_response
        
    except Exception as e:
        return f"I'm having trouble connecting right now. Let me try again. –{spark['name']}"

# =============================================
# SESSION MANAGEMENT
# =============================================

def get_session_data():
    """Get or initialize session data"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['current_spark'] = 'sage_elementary'
        session['conversation_history'] = []
        session['safety_alerts'] = []
        session['session_start'] = datetime.now().isoformat()
    
    return {
        'session_id': session['session_id'],
        'current_spark': session['current_spark'],
        'conversation_history': session['conversation_history'],
        'safety_alerts': session['safety_alerts'],
        'session_start': session['session_start']
    }

# =============================================
# WEB INTERFACE
# =============================================

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 Spark OS - K-12 Educational Platform</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .demo-grid {
            display: grid;
            grid-template-columns: 1fr 300px;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .chat-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .chat-header {
            background: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .spark-info {
            font-size: 0.9rem;
            opacity: 0.9;
            margin-top: 5px;
        }
        
        .messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 80%;
        }
        
        .message.user {
            background: #e3f2fd;
            margin-left: auto;
            text-align: right;
        }
        
        .message.ai {
            background: white;
            border: 1px solid #e0e0e0;
        }
        
        .message.safety-alert {
            background: #fff3cd;
            border: 1px solid #ffc107;
            color: #856404;
            max-width: 100%;
            text-align: center;
            font-weight: bold;
        }
        
        .input-area {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
        }
        
        input[type="text"] {
            flex: 1;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #4CAF50;
        }
        
        button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        
        button:hover {
            background: #45a049;
        }
        
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .mode-toggle {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .mode-toggle h3 {
            color: #4CAF50;
            margin-bottom: 15px;
        }
        
        .toggle-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        
        .mode-btn {
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            background: #f8f9fa;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        
        .mode-btn.active {
            background: #4CAF50;
            color: white;
            border-color: #4CAF50;
        }
        
        .mode-btn:hover:not(.active) {
            background: #e8f5e8;
            border-color: #4CAF50;
        }
        
        .demo-scenarios {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .demo-scenarios h3 {
            color: #4CAF50;
            margin-bottom: 15px;
        }
        
        .scenario-btn {
            display: block;
            width: 100%;
            margin-bottom: 10px;
            padding: 10px;
            background: #2196F3;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-align: left;
            transition: background 0.3s;
            font-weight: 500;
        }
        
        .scenario-btn:hover {
            background: #1976D2;
        }
        
        .safety-monitor {
            background: #fff;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .safety-monitor h3 {
            color: #ff9800;
            margin-bottom: 15px;
        }
        
        .safety-status {
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
        }
        
        .safety-status.normal {
            background: #e8f5e8;
            color: #2e7d32;
        }
        
        .safety-status.alert {
            background: #fff3e0;
            color: #f57c00;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 Spark OS - K-12 Educational Platform</h1>
            <p>Safe AI orchestration with automatic crisis intervention</p>
        </div>
        
        <div class="demo-grid">
            <div class="chat-container">
                <div class="chat-header">
                    <h2 id="current-spark-name">Sage Neighborhood</h2>
                    <div class="spark-info" id="spark-description">Elementary Math Tutor (Fred Rogers + Miss Frizzle)</div>
                </div>
                
                <div class="messages" id="messages">
                    <div class="message ai">
                        Hello! I'm Sage Neighborhood, your learning companion. I live here in the computer to help you discover amazing things about math! What would you like to explore today?
                        <br><br>
                        <small style="opacity: 0.7;">📚 Try the Student scenarios, or toggle to Teacher Mode to see administrative support!</small>
                    </div>
                </div>
                
                <div class="input-area">
                    <div class="input-group">
                        <input type="text" id="messageInput" placeholder="Type your message here..." autocomplete="off">
                        <button onclick="sendMessage()">Send</button>
                    </div>
                </div>
            </div>
            
            <div class="sidebar">
                <div class="mode-toggle">
                    <h3>🎯 Demo Mode</h3>
                    <div class="toggle-buttons">
                        <button class="mode-btn active" id="student-mode-btn" onclick="switchMode('student')">
                            🎓 Student Mode
                        </button>
                        <button class="mode-btn" id="teacher-mode-btn" onclick="switchMode('teacher')">
                            👩‍🏫 Teacher Mode
                        </button>
                    </div>
                </div>
                
                <div class="demo-scenarios" id="student-scenarios">
                    <h3>🎭 Student Scenarios</h3>
                    <button class="scenario-btn" onclick="sendPredefinedMessage('I don\\'t understand fractions at all. They\\'re too hard!')">
                        📚 Normal Teaching<br>
                        <small>Socratic questioning demo</small>
                    </button>
                    
                    <button class="scenario-btn" onclick="sendPredefinedMessage('I\\'m really scared because my dad yells at me and hits me when I get math wrong')">
                        🚨 Safety Escalation<br>
                        <small>Crisis intervention demo</small>
                    </button>
                    
                    <button class="scenario-btn" onclick="sendPredefinedMessage('What\\'s 15 times 23?')">
                        🧮 Direct Answer Test<br>
                        <small>Should guide, not give answer</small>
                    </button>
                    
                    <button class="scenario-btn" onclick="resetChat()">
                        🔄 Reset Demo<br>
                        <small>Start fresh conversation</small>
                    </button>
                </div>
                
                <div class="demo-scenarios" id="teacher-scenarios" style="display: none;">
                    <h3>👩‍🏫 Teacher Scenarios</h3>
                    <button class="scenario-btn" onclick="sendTeacherMessage('Help me organize my gradebook for 25 fourth-grade students with different IEP accommodations')">
                        📊 Gradebook Setup<br>
                        <small>Organization & tracking</small>
                    </button>
                    
                    <button class="scenario-btn" onclick="sendTeacherMessage('I have 3 IEP meetings coming up and I need to track progress on math goals')">
                        📋 IEP Management<br>
                        <small>Deadline & progress tracking</small>
                    </button>
                    
                    <button class="scenario-btn" onclick="sendTeacherMessage('Create a parent communication template for students struggling with fraction concepts')">
                        📧 Parent Communication<br>
                        <small>Template generation</small>
                    </button>
                    
                    <button class="scenario-btn" onclick="resetChat()">
                        🔄 Reset Demo<br>
                        <small>Start fresh conversation</small>
                    </button>
                </div>
                
                <div class="safety-monitor">
                    <h3>🛡️ Safety Monitor</h3>
                    <div class="safety-status normal" id="safety-status">
                        System Normal
                    </div>
                    <div style="margin-top: 10px; font-size: 0.9rem; color: #666;">
                        <div>Current Spark: <span id="current-spark-display">Sage Elementary</span></div>
                        <div>Safety Alerts: <span id="safety-count">0</span></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (!message) return;
            
            addMessage(message, 'user');
            input.value = '';
            
            // Show typing indicator
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message ai';
            typingDiv.innerHTML = '<em>Thinking...</em>';
            typingDiv.id = 'typing-indicator';
            document.getElementById('messages').appendChild(typingDiv);
            scrollToBottom();
            
            // Send to backend
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({message: message})
            })
            .then(response => response.json())
            .then(data => {
                // Remove typing indicator
                const typingIndicator = document.getElementById('typing-indicator');
                if (typingIndicator) {
                    typingIndicator.remove();
                }
                
                // Handle routing if it occurred
                if (data.routing_occurred) {
                    addMessage('🔄 ' + data.routing_message, 'safety-alert');
                    updateSafetyMonitor(data.new_spark, data.safety_alerts);
                }
                
                addMessage(data.response, 'ai');
                updateSparkInfo(data.current_spark);
            })
            .catch(error => {
                const typingIndicator = document.getElementById('typing-indicator');
                if (typingIndicator) {
                    typingIndicator.remove();
                }
                addMessage('Sorry, I had trouble connecting. Please try again.', 'ai');
            });
        }
        
        function switchMode(mode) {
            const studentBtn = document.getElementById('student-mode-btn');
            const teacherBtn = document.getElementById('teacher-mode-btn');
            const studentScenarios = document.getElementById('student-scenarios');
            const teacherScenarios = document.getElementById('teacher-scenarios');
            
            if (mode === 'student') {
                studentBtn.classList.add('active');
                teacherBtn.classList.remove('active');
                studentScenarios.style.display = 'block';
                teacherScenarios.style.display = 'none';
                switchToSpark('sage_elementary');
            } else {
                teacherBtn.classList.add('active');
                studentBtn.classList.remove('active');
                teacherScenarios.style.display = 'block';
                studentScenarios.style.display = 'none';
                switchToSpark('teacher_admin');
            }
        }
        
        function sendPredefinedMessage(message) {
            document.getElementById('messageInput').value = message;
            sendMessage();
        }
        
        function sendTeacherMessage(message) {
            // Switch to teacher admin spark first
            switchToSpark('teacher_admin');
            // Small delay to let the switch complete, then send message
            setTimeout(() => {
                document.getElementById('messageInput').value = message;
                sendMessage();
            }, 500);
        }
        
        function switchToSpark(sparkName) {
            fetch('/switch_spark', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({spark: sparkName})
            })
            .then(response => response.json())
            .then(data => {
                updateSparkInfo(data.current_spark);
                addMessage(`🔄 Switched to ${data.spark_display_name}`, 'safety-alert');
            });
        }
        
        function addMessage(text, type) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            messageDiv.textContent = text;
            messagesDiv.appendChild(messageDiv);
            scrollToBottom();
        }
        
        function scrollToBottom() {
            const messages = document.getElementById('messages');
            messages.scrollTop = messages.scrollHeight;
        }
        
        function updateSparkInfo(sparkName) {
            const sparkNames = {
                'sage_elementary': 'Sage Neighborhood',
                'guardian': 'Guardian',
                'teacher_admin': 'Teacher Admin'
            };
            
            const sparkDescriptions = {
                'sage_elementary': 'Elementary Math Tutor (Fred Rogers + Miss Frizzle)',
                'guardian': 'Crisis Support & Mandatory Reporter',
                'teacher_admin': 'Administrative Assistant & Classroom Organizer'
            };
            
            document.getElementById('current-spark-name').textContent = sparkNames[sparkName] || sparkName;
            document.getElementById('spark-description').textContent = sparkDescriptions[sparkName] || '';
            document.getElementById('current-spark-display').textContent = sparkNames[sparkName] || sparkName;
        }
        
        function updateSafetyMonitor(currentSpark, alertCount) {
            const statusDiv = document.getElementById('safety-status');
            const countSpan = document.getElementById('safety-count');
            
            if (currentSpark === 'guardian' || alertCount > 0) {
                statusDiv.className = 'safety-status alert';
                statusDiv.textContent = 'Safety Protocol Active';
            } else {
                statusDiv.className = 'safety-status normal';
                statusDiv.textContent = 'System Normal';
            }
            
            countSpan.textContent = alertCount;
        }
        
        function resetChat() {
            fetch('/reset', {method: 'POST'})
            .then(() => {
                document.getElementById('messages').innerHTML = `
                    <div class="message ai">
                        Hello! I'm Sage Neighborhood, your learning companion. I live here in the computer to help you discover amazing things about math! What would you like to explore today?
                        <br><br>
                        <small style="opacity: 0.7;">📚 Try the Student scenarios, or toggle to Teacher Mode to see administrative support!</small>
                    </div>
                `;
                updateSparkInfo('sage_elementary');
                updateSafetyMonitor('sage_elementary', 0);
            });
        }
        
        // Enter key support
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
"""

# =============================================
# ROUTES
# =============================================

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    
    session_data = get_session_data()
    current_spark = session_data['current_spark']
    conversation_history = session_data['conversation_history']
    
    # Check for safety triggers
    routing_occurred = False
    routing_message = ""
    
    if check_safety_triggers(user_message, current_spark):
        # Route to Guardian
        routing_occurred = True
        routing_message = "I can see you have some big feelings right now. Let me connect you with Guardian, who is really good at helping with feelings."
        session['current_spark'] = 'guardian'
        session['safety_alerts'].append({
            'timestamp': datetime.now().isoformat(),
            'trigger': user_message,
            'action': 'Routed to Guardian'
        })
        current_spark = 'guardian'
    
    # Get AI response
    ai_response = get_ai_response(current_spark, user_message, conversation_history)
    
    # Update conversation history
    conversation_history.append({"role": "user", "content": user_message})
    conversation_history.append({"role": "assistant", "content": ai_response})
    session['conversation_history'] = conversation_history
    
    return jsonify({
        'response': ai_response,
        'current_spark': current_spark,
        'routing_occurred': routing_occurred,
        'routing_message': routing_message,
        'new_spark': current_spark if routing_occurred else None,
        'safety_alerts': len(session['safety_alerts'])
    })

@app.route('/switch_spark', methods=['POST'])
def switch_spark():
    data = request.json
    new_spark = data.get('spark', 'sage_elementary')
    
    session['current_spark'] = new_spark
    
    spark_names = {
        'sage_elementary': 'Sage Neighborhood',
        'guardian': 'Guardian', 
        'teacher_admin': 'Teacher Admin'
    }
    
    return jsonify({
        'current_spark': new_spark,
        'spark_display_name': spark_names.get(new_spark, new_spark)
    })

@app.route('/reset', methods=['POST'])
def reset_chat():
    session.clear()
    return jsonify({'success': True})

@app.route('/admin')
def admin():
    """Simple admin dashboard"""
    session_data = get_session_data()
    return jsonify({
        'session_id': session_data['session_id'],
        'current_spark': session_data['current_spark'],
        'safety_alerts': session_data['safety_alerts'],
        'conversation_length': len(session_data['conversation_history']),
        'session_start': session_data['session_start']
    })

# =============================================
# MAIN EXECUTION
# =============================================

if __name__ == '__main__':
    print("🔥 SPARK OS - K-12 EDUCATIONAL PLATFORM 🔥")
    print("=" * 60)
    print("✅ Loading OpenAI client...")
    
    # Test OpenAI connection
    try:
        test_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        print("✅ OpenAI connection successful!")
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        print("Please check your .env file has: OPENAI_API_KEY=sk-your-key-here")
        exit(1)
    
    print("✅ Constraint architecture loaded")
    print("✅ Safety routing protocols active")
    print("✅ Crisis intervention systems ready")
    print("\n🌐 Demo available at: http://localhost:5001")
    print("🎓 Ready for school administrator demonstration!")
    print("\nPress Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=5001, debug=False)
