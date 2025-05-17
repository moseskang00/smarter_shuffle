-- This file is NOT executed, 
-- it's just a reference for the schema



-- Users table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    spotify_id TEXT UNIQUE NOT NULL,
    display_name TEXT,
    email TEXT UNIQUE,
    country TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
);

-- Sessions table
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    access_token TEXT NOT NULL,
    refresh_token TEXT NOT NULL,
    token_expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
);

-- Songs table
CREATE TABLE songs (
    song_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    spotify_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    album TEXT,
    release_year INTEGER,
    genres TEXT[],

    -- Audio features
    danceability FLOAT4,
    energy FLOAT4,
    tempo FLOAT4,
    valence FLOAT4,
    acousticness FLOAT4,
    instrumentalness FLOAT4,
    popularity INTEGER,
    preview_url TEXT,
    spotify_url TEXT,
);

-- Listening Events table
CREATE TABLE listening_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    song_id UUID NOT NULL,
    listened_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    duration_listened INTEGER NOT NULL, -- in milliseconds
    skip_time INTEGER, -- in milliseconds, NULL if not skipped
    likability_score FLOAT, -- calculated score based on skip time
);

-- Indexes for better query performance
CREATE INDEX idx_listening_events_user_id ON listening_events(user_id);
CREATE INDEX idx_listening_events_song_id ON listening_events(song_id);
CREATE INDEX idx_listening_events_listened_at ON listening_events(listened_at);
CREATE INDEX idx_songs_spotify_id ON songs(spotify_id);
CREATE INDEX idx_users_spotify_id ON users(spotify_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers to automatically update updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_songs_updated_at
    BEFORE UPDATE ON songs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column(); 