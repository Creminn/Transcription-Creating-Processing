# Whisper API Server

Standalone Whisper transcription service that can be hosted on a remote server and accessed via Tailscale.

## Setup on Remote Server

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install FFmpeg (Required for Whisper)

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg
```

### 3. Configure Tailscale

```bash
# Install Tailscale (if not already installed)
# Ubuntu/Debian
curl -fsSL https://tailscale.com/install.sh | sh

# macOS
brew install tailscale

# Start Tailscale
sudo tailscale up

# Note your Tailscale IP address
tailscale ip -4
```

### 4. Run the Server

```bash
# Basic run
python app.py

# Or with uvicorn directly
uvicorn app:app --host 0.0.0.0 --port 8001

# With environment variables
WHISPER_HOST=0.0.0.0 WHISPER_PORT=8001 python app.py
```

### 5. Run as a Service (Optional)

Create a systemd service file `/etc/systemd/system/whisper-api.service`:

```ini
[Unit]
Description=Whisper API Server
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/whisper-server
Environment="PATH=/path/to/whisper-server/venv/bin"
ExecStart=/path/to/whisper-server/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable and start:

```bash
sudo systemctl enable whisper-api
sudo systemctl start whisper-api
sudo systemctl status whisper-api
```

## Usage

### Health Check

```bash
curl http://<tailscale-ip>:8001/health
```

### Transcribe Audio File

```bash
curl -X POST "http://<tailscale-ip>:8001/transcribe" \
  -F "file=@audio.mp3" \
  -F "model_size=base" \
  -F "language=en"
```

### Transcribe from URL

```bash
curl -X POST "http://<tailscale-ip>:8001/transcribe/url" \
  -F "audio_url=http://<tailscale-ip>:8000/storage/audio/file.mp3" \
  -F "model_size=base" \
  -F "language=en"
```

## Model Sizes

- `tiny` - Fastest, least accurate (~39M parameters)
- `base` - Balanced (default, ~74M parameters)
- `small` - Better accuracy (~244M parameters)
- `medium` - High accuracy (~769M parameters)
- `large` - Best accuracy (~1550M parameters)

## GPU Support

If you have a GPU with CUDA:

```bash
# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Use GPU by setting device parameter
curl -X POST "http://<tailscale-ip>:8001/transcribe" \
  -F "file=@audio.mp3" \
  -F "model_size=base" \
  -F "device=cuda"
```

## Security Notes

1. **Tailscale**: This service is accessible only on your Tailscale network, providing secure access without exposing to the public internet.

2. **Firewall**: Consider restricting access to Tailscale IPs only:
   ```bash
   sudo ufw allow from 100.64.0.0/10 to any port 8001
   ```

3. **Authentication**: For production, consider adding API key authentication to the service.

## Troubleshooting

### Model Download Issues
Models are automatically downloaded on first use. They're cached in `~/.cache/whisper/`.

### Memory Issues
- Use smaller models (`tiny` or `base`)
- Process files sequentially
- Consider GPU if available

### Connection Issues
- Verify Tailscale is running: `tailscale status`
- Check firewall rules
- Test connectivity: `ping <tailscale-ip>`
