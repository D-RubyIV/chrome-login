# Chrome Profile Manager

A FastAPI-based application for managing multiple Chrome browser profiles with proxy support.

## Overview

This project provides an API to create, manage, and launch Chrome browser profiles with custom configurations. It supports proxy settings and allows for multiple isolated browser instances.

## Features

- Create new Chrome profiles
- List existing profiles
- Open profiles with custom configurations
- Update profile settings (proxy, notes)
- Automatic port management
- Proxy extension support
- Chrome version compatibility handling

## Prerequisites

- Python 3.x
- Google Chrome browser installed at `C:\Program Files\Google\Chrome\Application\chrome.exe`
- Required Python packages (install via pip):
  - fastapi
  - pydantic
  - uvicorn

## Project Structure

```
.
├── api/
│   ├── api.py          # Main API endpoints
│   ├── body.py         # Request models
│   └── proxyAuth.py    # Proxy authentication handling
├── data/
│   └── user/
│       └── profiles/   # Chrome profile data storage
├── equipment/
│   ├── alchemy.py      # Database utilities
│   └── models.py       # Database models
├── service/
│   └── profile/
│       └── profileservice.py  # Profile management service
└── utils/
    ├── chrome.py       # Chrome-related utilities
    └── profile.py      # Profile utilities
```

## API Endpoints

### 1. List Profiles
- **GET** `/api/v1/profiles`
- Returns a list of all available profiles

### 2. Get Profile Details
- **GET** `/api/v1/profiles/{profile_id}`
- Returns details of a specific profile and launches Chrome with that profile

### 3. Create Profile
- **POST** `/api/v1/profiles`
- Creates a new Chrome profile
- Request body:
  ```json
  {
    "profile_name": "string",
    "raw_proxy": "string"
  }
  ```

### 4. Update Profile
- **PUT** `/api/v1/profiles/{profile_id}`
- Updates profile settings
- Request body:
  ```json
  {
    "raw_proxy": "string",
    "raw_note": "string"
  }
  ```

## Response Format

All API responses follow this structure:
```json
{
  "success": boolean,
  "data": object | null,
  "message": string
}
```

## Chrome Profile Configuration

When launching a profile, the following Chrome flags are set:
- Remote debugging port (automatically assigned)
- Language: Vietnamese
- Audio muted
- No first run
- No default browser check
- Window size: 400x880
- Window position: 0,0
- Device scale factor: 0.6
- Custom user data directory
- Profile directory: Default
- Session restore disabled

## Proxy Support

The system supports proxy configuration through Chrome extensions. When a proxy is specified:
1. A proxy extension is created in the profile's extension directory
2. The extension is loaded when launching Chrome
3. Proxy settings are applied automatically

## Error Handling

The API includes comprehensive error handling for:
- Profile not found (404)
- Server errors (500)
- Invalid requests
- Chrome launch failures

## Security Considerations

- Profiles are isolated in separate directories
- Each profile has its own user data directory
- Proxy credentials are stored securely
- Port management prevents conflicts

## Development

To run the development server:
```bash
"python" "main.py"
```