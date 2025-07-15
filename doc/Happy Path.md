# Happy Path: MoVi Prototype Roadmap

This document outlines the core development stages for delivering a working prototype of MoVi, a semantic, vibe-based movie discovery platform.

Each step results in a functional system that builds on the previous, culminating in a full-stack prototype.

---

## Step 1: Django Backend MVP (Text Search)

🎯 **Goal**: Minimal backend service with movie storage and basic search

### Features
- Django REST Framework setup
- PostgreSQL integration
- `Movie` model:
  - Title, synopsis, release year, genre, tags, poster URL
- Endpoints:
  - `GET /movies/` - list all
  - `GET /movies/<id>/` - get details
  - `GET /movies/search/?q=` - text search on title/synopsis
  - `POST /movies/` - add movie manually
- Optional: `GET /movies/import/?q=` - search TMDB API and import

### Output
- All routes tested via Postman
- Data stored in PostgreSQL

---

## Step 2: Vector Search Integration (Qdrant)

🎯 **Goal**: Enable semantic search using embeddings

### Features
- Integrate SentenceTransformers (`all-MiniLM-L6-v2`)
- Generate embedding on movie creation
- Qdrant setup with Docker
- Endpoints:
  - `GET /movies/vibesearch/?q=` - semantic search by vibe
  - `POST /movies/<id>/embed/` - regenerate embedding manually
- Management command to backfill embeddings

### Output
- Semantic movie search enabled
- Postman-tested flow

---

## Step 3: User Features & Review System

🎯 **Goal**: Introduce user interaction and enriched filtering

### Features
- User registration & login (JWT)
- `Review` model: rating, comment
- `Tag` model: user-submitted or system-suggested
- Improved search filters:
  - genre, rating, tags, release year

### Output
- Users can leave reviews and filter search results
- Review & rating data influence search

---

## Step 4: Frontend Web App

🎯 **Goal**: Build a usable web interface

### Features
- React-based frontend (or framework of choice)
- Pages:
  - Movie Search
  - Movie Detail
  - User Login/Register
  - Review Submission
- Calls Django backend via REST API

### Output
- Usable full-stack prototype
- Dockerized for deployment

---

## Optional Future Steps

- Admin moderation tools
- Full-text search via PostgreSQL FTS or Elasticsearch
- Recommendation engine via user similarity
- UI themes (light/dark)
