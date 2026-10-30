# End-to-End Book Recommender System

A book recommendation application built with Python, pandas, scikit-learn, and Streamlit. It uses ratings from the Book-Crossing dataset to find books with rating patterns similar to a selected title, then displays up to five recommendations with their cover images.

This repository includes the application code and training pipeline. The dataset and trained model are generated or downloaded when training runs; they are not required to launch the Streamlit interface, but training must complete before recommendations can be requested.

## Contents

- [How it works](#how-it-works)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Install and run on Windows](#install-and-run-on-windows)
- [Install and run on macOS or Linux](#install-and-run-on-macos-or-linux)
- [Run with Docker](#run-with-docker)
- [Train the recommender](#train-the-recommender)
- [Use the application](#use-the-application)
- [Dataset and preprocessing](#dataset-and-preprocessing)
- [Generated files](#generated-files)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Notes for contributors](#notes-for-contributors)

## How it works

The project implements an item-based collaborative-filtering recommender:

1. The ingestion stage downloads a ZIP archive from the URL in `config/config.yaml` and extracts it.
2. The validation stage reads the book and rating CSV files, keeps users with more than 200 ratings, joins ratings to book metadata, keeps titles with at least 50 ratings, and removes duplicate user/title pairs.
3. The transformation stage creates a book-by-user ratings table. Missing ratings are filled with zero.
4. The model trainer fits scikit-learn's `NearestNeighbors` model using the book rating vectors and saves it for the application.
5. The Streamlit app finds the six nearest book rows for a selected title. The selected book itself is the nearest result, so the interface displays the other five.

The recommendation model uses ratings rather than book descriptions or text. Cover images come from the `Image-URL-L` field in the dataset. Recommendations can still be shown when a matching image URL is unavailable; the cover is simply omitted.

## Project structure

```text
.
├── app.py                                  # Streamlit application and recommendation interface
├── config/
│   └── config.yaml                         # Dataset URL and pipeline directory settings
├── books_recommender_system/
│   ├── components/
│   │   ├── stage_00_data_ingestion.py      # Download and extract the dataset
│   │   ├── stage_01_data_validation.py     # Clean and filter the input data
│   │   ├── stage_02_data_transformation.py  # Build the book-by-user rating matrix
│   │   └── stage_03_model_trainer.py        # Fit and save nearest-neighbor model
│   ├── config/configuration.py             # Builds component configuration objects
│   ├── constant/                           # Shared configuration path constants
│   ├── entity/config_entity.py             # Configuration object definitions
│   ├── exception/exception_handler.py      # Application exception formatting
│   ├── logger/log.py                       # File logging setup
│   ├── pipeline/training_pipeline.py       # Runs all four training stages in order
│   └── utils/util.py                       # YAML configuration reader
├── templates/
│   └── book_names.pkl                      # Book titles used by the selection menu
├── notebook/
│   └── research.ipynb                      # Exploratory analysis notebook
├── requirements.txt                        # Python dependencies
├── setup.py                                # Package metadata and dependencies
├── Dockerfile                              # Container image for the Streamlit app
├── .dockerignore                           # Files excluded from the Docker build context
└── README.md
```

Training creates an `artifacts/` directory and a `logs/` directory at runtime. They are not source code. The root-level `books_data.zip`, if you have one, is ignored by Git and is not read directly by the current ingestion code: the pipeline downloads the configured URL into `artifacts/dataset/raw_data/` each time it trains.

## Requirements

- Python 3.10 or newer; Python 3.12 has been used with this project.
- Git, if cloning the repository.
- An internet connection when running the training pipeline, because the pipeline downloads its dataset from the configured URL.
- Enough disk space for the downloaded dataset, extracted CSV files, intermediate data, and model artifacts.

Run commands from the repository root. The application and configuration use paths relative to the current working directory.

## Install and run on Windows

Open PowerShell in the project directory. Create and activate a virtual environment:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation scripts, either use a terminal where activation is allowed or call the environment's executables directly as shown below.

Install the project dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Start the application:

```powershell
python -m streamlit run app.py
```

If you are using the existing `vnev_00` virtual environment in this checkout instead of creating `.venv`, run:

```powershell
.\vnev_00\Scripts\python.exe -m streamlit run app.py
```

Streamlit prints a local address in the terminal, usually `http://localhost:8501`, and may open it in your browser.

## Install and run on macOS or Linux

From the repository root, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies and start Streamlit:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

## Run with Docker

Install and start Docker Desktop (Windows or macOS) or the Docker Engine (Linux), then run these commands from the repository root:

```bash
docker build -t book-recommender .
docker run --name book-recommender -p 8501:8501 -v book-recommender-artifacts:/app/artifacts -v book-recommender-logs:/app/logs book-recommender
```

Open `http://localhost:8501` in a browser. Click **Train Recommender System** and wait for training to finish before requesting recommendations. The container needs internet access for the configured dataset download. The named Docker volumes keep generated artifacts and logs when the container is removed or replaced.

To stop the running container, press `Ctrl+C` in its terminal, or run `docker stop book-recommender` in another terminal. To start the existing stopped container again, use `docker start -ai book-recommender`.

The image uses Python 3.12 and contains the app code, configuration, dependencies, and title list. `.dockerignore` excludes local environments, secrets, logs, notebooks, archives, and generated artifacts from the build context. If you rebuild the image, existing artifacts in Docker volumes remain separate from the image.

## Train the recommender

The first run requires model artifacts. After starting the app:

1. Click **Train Recommender System**.
2. Keep the application running while the pipeline downloads the dataset, processes it, and fits the model. The initial run can take several minutes depending on network speed and computer performance.
3. Wait for **Training Completed!** before requesting recommendations.
4. Click **Show Recommendation**.

Training is synchronous in the Streamlit app, so the page may appear busy while the pipeline is running. Avoid starting multiple training runs at once. Training downloads the dataset again on each run with the current implementation.

The pipeline can also be started from the repository root in a Python environment with the requirements installed:

```bash
python -c "from books_recommender_system.pipeline.training_pipeline import TrainingPipeline; TrainingPipeline().start_training_pipeline()"
```

The command above runs ingestion, validation, transformation, and model training in order. It also needs network access to download the dataset.

## Use the application

1. Start Streamlit from the repository root.
2. Train the recommender if the model has not yet been generated.
3. Choose a title from the dropdown or type to filter the list.
4. Click **Show Recommendation**.
5. The application displays up to five similar titles and their available cover images.

If the model file is missing, the app displays a message asking you to train before showing recommendations. The selection list is loaded from `templates/book_names.pkl`.

## Dataset and preprocessing

The default dataset URL is configured in `config/config.yaml`. The archive is expected to contain:

- `BX-Books.csv`: book metadata, including title, author, publisher, ISBN, and cover image URLs.
- `BX-Book-Ratings.csv`: user IDs, ISBNs, and ratings.
- `BX-Users.csv`: user information. The current model pipeline does not use this file.

The CSV files use semicolons as separators and Latin-1 encoding. Malformed rows are skipped when they are read. The validation stage applies these filters:

- Keep users with more than 200 ratings.
- Join ratings to books using ISBN.
- Keep books with at least 50 ratings after filtering users.
- Remove duplicate ratings for the same user and title.

The thresholds are currently written in `stage_01_data_validation.py`. The dataset URL, archive directory names, CSV names, and artifact directory names are in `config/config.yaml`.

## Generated files

The training pipeline writes these outputs under `artifacts/`:

```text
artifacts/
├── dataset/
│   ├── raw_data/books_data.zip
│   ├── ingested_data/                       # Extracted CSV files
│   ├── clean_data/clean_data.csv
│   └── transformed_data/transformed_data.pkl
├── serialized_objects/
│   ├── book_names.pkl
│   ├── book_pivot.pkl
│   └── final_rating.pkl
└── trained_model/model.pkl
```

Logs are written to timestamped files under `logs/`. Re-running training recreates the output files. Do not load pickle files from sources you do not trust; Python pickle files can execute code when loaded.

## Configuration

Edit `config/config.yaml` to change the dataset URL or output directory names. The configuration is read when the application and pipeline components are initialized. The current app expects to be launched with the repository root as its working directory, so relative paths in the configuration resolve correctly.

The `recommendation_config.poster_api_url` value is present in the YAML file, but the current application does not call that API. Poster images are read directly from the dataset's `Image-URL-L` column.

## Troubleshooting

### “The recommender model has not been trained yet”

Click **Train Recommender System** and wait for **Training Completed!**. The model must exist at `artifacts/trained_model/model.pkl` before recommendations can be made.

### The training pipeline cannot download the dataset

Check your internet connection and the `dataset_download_url` value in `config/config.yaml`. The current pipeline downloads from that URL on every training run; it does not use a root-level `books_data.zip` as a cache.

### `ModuleNotFoundError` when starting the app

Activate the virtual environment where the project dependencies were installed, then run `pip install -r requirements.txt` in that same environment. In VS Code, select that environment as the Python interpreter and use its terminal.

### A file or directory cannot be found

Start the command from the repository root, where `app.py` and `config/config.yaml` are located. Check that the expected input CSV files were extracted under `artifacts/dataset/ingested_data/` and that training completed successfully.

### Recommendations fail after interrupted training

If training was interrupted, run it again and wait for the completion message. Check the newest file in `logs/` for pipeline details. The model and serialized objects are produced in successive stages, so an interrupted run may leave some outputs but not the complete set.

### Cover images are missing

Some dataset rows may have an empty or unavailable image URL. The recommendation itself can still be displayed without a cover image.

## Notes for contributors

- Keep generated model files, downloaded datasets, virtual environments, logs, and credentials out of source commits unless there is a clear reason to distribute them.
- `books_data.zip`, `.env`, `vnev_00/`, and the notebook's local data directory are ignored by the current `.gitignore`.
- If you choose to commit the dataset, check its redistribution terms and GitHub's file-size limits first. Large files may need Git Large File Storage.
- Dependencies are listed in `requirements.txt` and in `setup.py`. When changing runtime imports, update the dependency lists as needed.
- The Docker image does not contain a pre-trained model. Train it from the app after starting the container; use named volumes if you want generated model files to persist.
