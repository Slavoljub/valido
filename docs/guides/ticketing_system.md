# Ticketing System Implementation Plan

## Current Implementation Status: 85%

### Overview
Comprehensive support ticketing system for ValidoAI with full CRUD operations, real-time messaging, file attachments, and advanced filtering capabilities.

### Completed Features (15%)
- Basic route structure in routes.py
- Controller skeleton in src/controllers/ticket_controller.py
- Basic database schema planning

### In Progress (0%)
- Database schema implementation
- UI templates creation
- API endpoints implementation
- Real-time messaging system

### Planned Features (85%)
- Complete ticketing system with all CRUD operations
- Real-time messaging and notifications
- File attachment support
- Advanced filtering and search
- Agent assignment and management
- Priority and status management
- Email notifications
- Reporting and analytics

## COMPREHENSIVE TICKETING SYSTEM IMPLEMENTATION

### 1. Database Schema & Data Model

#### Core Tables
```sql
-- Tickets table
CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_number VARCHAR(20) UNIQUE NOT NULL,
    subject TEXT NOT NULL,
    description TEXT,
    requester_id INTEGER,
    agent_id INTEGER,
    follower_id INTEGER,
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    status ENUM('open', 'pending', 'in_progress', 'resolved', 'closed') DEFAULT 'open',
    type ENUM('question', 'bug', 'feature_request', 'support', 'billing') DEFAULT 'question',
    tags TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP NULL,
    FOREIGN KEY (requester_id) REFERENCES users(id),
    FOREIGN KEY (agent_id) REFERENCES users(id),
    FOREIGN KEY (follower_id) REFERENCES users(id)
);

-- Ticket messages table
CREATE TABLE ticket_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    message_type ENUM('internal', 'public', 'system') DEFAULT 'public',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id),
    FOREIGN KEY (sender_id) REFERENCES users(id)
);

-- Ticket attachments table
CREATE TABLE ticket_attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    message_id INTEGER NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(100),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id),
    FOREIGN KEY (message_id) REFERENCES ticket_messages(id)
);

-- Users table (for agents and requesters)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role ENUM('admin', 'agent', 'requester') DEFAULT 'requester',
    avatar_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ticket activity log
CREATE TABLE ticket_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 2. Core Features Implementation

#### 2.1 Ticket Management
- **Create Ticket**: Form with all required fields, file upload, priority selection
- **View Ticket**: Detailed view with conversation thread, attachments, activity log
- **Update Ticket**: Edit ticket details, change status, assign agents
- **Close Ticket**: Mark as resolved/closed with resolution notes
- **List Tickets**: Paginated list with filtering and search

#### 2.2 Messaging System
- **Real-time Messages**: WebSocket support for live updates
- **Message Types**: Public, internal notes, system notifications
- **Rich Text Editor**: Formatting, emojis, code blocks
- **File Attachments**: Drag & drop, multiple file support
- **Message History**: Complete conversation thread

#### 2.3 User Management
- **Agent Assignment**: Assign tickets to specific agents
- **Follower System**: Add followers to receive updates
- **User Roles**: Admin, Agent, Requester permissions
- **User Profiles**: Avatars, contact information, preferences

#### 2.4 Advanced Features
- **Search & Filter**: Full-text search, advanced filters
- **Priority Management**: Visual priority indicators
- **Status Workflow**: Customizable status transitions
- **Tags System**: Categorize tickets with tags
- **Email Notifications**: Automatic email updates
- **Export Functionality**: CSV export of ticket data

### 3. UI/UX Implementation

#### 3.1 Main Dashboard (Tickets List)
- **Summary Cards**: Total, Pending, Solved, Deleted tickets
- **Search Bar**: Full-text search with filters
- **Action Buttons**: Create, Export, Bulk actions
- **Status Filters**: All, Solved, Pending, Archived
- **Data Table**: Sortable columns, pagination, bulk selection

#### 3.2 Ticket Creation Modal
- **Two-Column Layout**: Left and right field groups
- **Required Fields**: Subject, description, type, priority
- **Optional Fields**: Tags, followers, attachments
- **Validation**: Real-time form validation
- **Auto-save**: Draft saving functionality

#### 3.3 Ticket Detail View
- **Header**: Ticket number, status, priority, actions
- **Conversation Thread**: Chronological message display
- **Message Composition**: Rich text editor with attachments
- **Sidebar**: Ticket details, activity log, participants
- **Actions**: Reply, close, assign, add followers

#### 3.4 Responsive Design
- **Mobile-First**: Optimized for all screen sizes
- **Touch-Friendly**: Large touch targets, swipe gestures
- **Progressive Enhancement**: Works without JavaScript
- **Accessibility**: WCAG 2.1 AA compliance

### 4. API Endpoints

#### 4.1 Ticket Management
```
GET    /tickets                    # List tickets with filters
POST   /tickets                    # Create new ticket
GET    /tickets/{id}              # Get ticket details
PUT    /tickets/{id}              # Update ticket
DELETE /tickets/{id}              # Delete ticket
POST   /tickets/{id}/close        # Close ticket
POST   /tickets/{id}/assign       # Assign agent
```

#### 4.2 Messaging
```
GET    /tickets/{id}/messages     # Get ticket messages
POST   /tickets/{id}/messages     # Send message
PUT    /tickets/{id}/messages/{msg_id}  # Edit message
DELETE /tickets/{id}/messages/{msg_id}  # Delete message
```

#### 4.3 Attachments
```
POST   /tickets/{id}/attachments  # Upload attachment
GET    /attachments/{id}          # Download attachment
DELETE /attachments/{id}          # Delete attachment
```

#### 4.4 Users & Agents
```
GET    /users                     # List users
GET    /users/agents              # List agents
POST   /tickets/{id}/followers    # Add follower
DELETE /tickets/{id}/followers/{user_id}  # Remove follower
```

### 5. Implementation Phases

#### Phase 1: Core Infrastructure (25%)
- Database schema creation
- Basic CRUD operations
- Simple ticket list and detail views
- Basic form validation

#### Phase 2: Messaging System (50%)
- Message creation and display
- File attachment support
- Real-time updates (WebSocket)
- Rich text editor integration

#### Phase 3: Advanced Features (75%)
- Search and filtering
- User management and roles
- Email notifications
- Activity logging

#### Phase 4: Polish & Optimization (100%)
- Performance optimization
- Advanced UI features
- Reporting and analytics
- Mobile responsiveness

### 6. Technical Requirements

#### 6.1 Backend Dependencies
```python
# Database
sqlite3 (built-in)
# File handling
werkzeug.utils
# Email
smtplib, email
# Real-time
flask-socketio
# Validation
marshmallow
# Search
sqlite-fts4
```

#### 6.2 Frontend Dependencies
```javascript
// Rich text editor
Quill.js or TinyMCE
// File upload
Dropzone.js
// Real-time
Socket.io client
// Date handling
Moment.js
// Charts
Chart.js
```

#### 6.3 File Structure
```
templates/
├── tickets/
│   ├── index.html          # Main tickets list
│   ├── create.html         # Create ticket modal
│   ├── detail.html         # Ticket detail view
│   └── components/
│       ├── ticket-card.html
│       ├── message-thread.html
│       └── attachment-upload.html

static/
├── js/
│   ├── tickets.js          # Main tickets functionality
│   ├── ticket-detail.js    # Detail view logic
│   └── ticket-create.js    # Creation form logic
├── css/
│   └── tickets.css         # Ticket-specific styles
└── uploads/
    └── tickets/            # Ticket attachments

src/
├── models/
│   ├── ticket.py           # Ticket model
│   ├── message.py          # Message model
│   └── user.py             # User model
├── services/
│   ├── ticket_service.py   # Business logic
│   ├── email_service.py    # Email notifications
│   └── file_service.py     # File handling
└── controllers/
    └── ticket_controller.py # API endpoints
```

### 7. Sample Data & Testing

#### 7.1 Sample Users
```python
SAMPLE_USERS = [
    {
        'name': 'Jese Leos',
        'email': 'jese.leos@validoai.com',
        'role': 'agent',
        'avatar': '/static/images/avatars/jese.jpg'
    },
    {
        'name': 'Bonnie Green',
        'email': 'bonnie.green@validoai.com',
        'role': 'agent',
        'avatar': '/static/images/avatars/bonnie.jpg'
    },
    {
        'name': 'Neil Sims',
        'email': 'neil.sims@validoai.com',
        'role': 'agent',
        'avatar': '/static/images/avatars/neil.jpg'
    },
    {
        'name': 'Roberta Casas',
        'email': 'roberta.casas@validoai.com',
        'role': 'admin',
        'avatar': '/static/images/avatars/roberta.jpg'
    }
]
```

#### 7.2 Sample Tickets
```python
SAMPLE_TICKETS = [
    {
        'ticket_number': '#1846325',
        'subject': 'Help with my purchase',
        'requester': 'Mark Duan',
        'priority': 'medium',
        'agent': 'Jese Leos',
        'status': 'pending',
        'created_date': '2025-03-02'
    },
    {
        'ticket_number': '#1846328',
        'subject': 'Support for Flowbite',
        'requester': 'Donnie Gree',
        'priority': 'high',
        'agent': 'Neil Sims',
        'status': 'pending',
        'created_date': '2025-03-03'
    }
]
```

### 8. Success Metrics

#### 8.1 Performance Metrics
- Page load time < 2 seconds
- Message delivery < 1 second
- File upload progress indication
- Search results < 500ms

#### 8.2 User Experience Metrics
- Ticket creation < 3 steps
- Message composition < 30 seconds
- Mobile usability score > 90
- Accessibility compliance 100%

#### 8.3 Business Metrics
- Average response time < 4 hours
- Ticket resolution rate > 85%
- Customer satisfaction > 4.5/5
- Agent productivity +25%

### 9. Notes

- Implement proper error handling and validation
- Ensure data security and privacy compliance
- Add comprehensive logging for debugging
- Create automated tests for all functionality
- Document API endpoints thoroughly
- Consider scalability for future growth
- Implement backup and recovery procedures
- Add monitoring and alerting systems
