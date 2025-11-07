# llm_zoomcamp
learning


## useful shell command
docker run -it --rm \
    --network="llm_zoomcamp_default" \
    --env-file=".env" \
    -e GROQ_API_KEY=${GROQ_API_KEY} \
    -e DATA_PATH="data/data.csv" \
    -p 5000:5000 \
    app



pipenv shell

cd app/

export POSTGRES_HOST=localhost
python app.py



docker run -it --rm app bash
ls -R /app
python - <<'EOF'
from pathlib import Path
print(list(Path("/app/data").glob("*")))
EOF

## run streamlit

export POSTGRES_HOST=localhost
export BACKEND_URL="http://localhost:5000"
streamlit run streamlit_app.py
