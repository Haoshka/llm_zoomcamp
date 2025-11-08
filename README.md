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

## initialize db
pipenv shell

cd app

export POSTGRES_HOST=localhost
python db_prep.py


## run the app from virtual env
pipenv shell

cd app

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


## run grafana
pipenv shell 
cd grafana 
# make sure the POSTGRES_HOST variable is not overwritten 
env | grep POSTGRES_HOST 
python init.py


## check csv file

docker exec -it <container id> bash ls data/