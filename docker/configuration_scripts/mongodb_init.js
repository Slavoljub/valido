// MongoDB Initialization Script

print('Initializing MongoDB...');

// Create database and collections
db = db.getSiblingDB('ai_valido_online');

// Create collections
db.createCollection('users');
db.createCollection('documents');
db.createCollection('sessions');

// Create indexes
db.users.createIndex({ "email": 1 }, { unique: true });
db.documents.createIndex({ "created_at": 1 });
db.sessions.createIndex({ "expires_at": 1 }, { expireAfterSeconds: 0 });

// Insert sample data
db.users.insertOne({
    email: "admin@validoai.com",
    name: "Admin User",
    role: "admin",
    created_at: new Date()
});

print('MongoDB initialization completed');
