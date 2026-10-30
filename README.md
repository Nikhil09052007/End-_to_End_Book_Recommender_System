# End-to-End Book Recommender System

A book recommendation application built with Python, pandas, scikit-learn, and Streamlit. It uses ratings from the Book-Crossing dataset to find books with rating patterns similar to a selected title, then displays up to five recommendations with their cover images.

This repository includes the application, training pipeline, and the small pre-trained files needed to show recommendations immediately. Raw data and intermediate training outputs are generated locally and excluded from Git to keep the repository easier to clone and deploy. Retraining downloads the source dataset from the URL in `config/config.yaml`.

**Live application:** [Open the Book Recommender](https://end-toendbookrecommendersystem-qus538syamkw4baswuwdzq.streamlit.app/)

## Contents

- [Live application](#live-application)
- [How it works](#how-it-works)
- [Project structure](#project-structure)
- [Requirements](#requirements)
- [Install and run on Windows](#install-and-run-on-windows)
- [Install and run on macOS or Linux](#install-and-run-on-macos-or-linux)
- [Deploy on Streamlit Community Cloud](#deploy-on-streamlit-community-cloud)
- [Run with Docker](#run-with-docker)
- [Train or refresh the recommender](#train-or-refresh-the-recommender)
- [Use the application](#use-the-application)
- [Dataset and preprocessing](#dataset-and-preprocessing)
- [Generated files](#generated-files)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Notes for contributors](#notes-for-contributors)

## Live application

Try the deployed Streamlit app here: [https://end-toendbookrecommendersystem-qus538syamkw4baswuwdzq.streamlit.app/](https://end-toendbookrecommendersystem-qus538syamkw4baswuwdzq.streamlit.app/).

Choose a book from the selection menu and click **Show Recommendation** to see up to five similar titles and their available cover images. The application uses the pre-trained recommendation files included in this project, so visitors do not need to download the dataset or train the model themselves.

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
├── artifacts/
│   ├── serialized_objects/
│   │   ├── book_pivot.pkl                   # Book/user rating matrix for inference
│   │   └── final_rating.pkl                 # Titles and cover image URLs
│   └── trained_model/
│       └── model.pkl                        # Pre-trained nearest-neighbor model
├── notebook/
│   └── research.ipynb                      # Exploratory analysis notebook
├── requirements.txt                        # Python dependencies
├── setup.py                                # Package metadata and dependencies
├── Dockerfile                              # Container image for the Streamlit app
├── .dockerignore                           # Files excluded from the Docker build context
└── README.md
```

The inference files shown above are included so a deployed app can work immediately. Training creates additional files under `artifacts/dataset/` and `artifacts/serialized_objects/`, as well as timestamped files under `logs/`; these are generated outputs ignored by Git. The root-level `books_data.zip`, if present, is also ignored and is not read directly by the current ingestion code: training downloads the configured URL into `artifacts/dataset/raw_data/` each time it runs.

## Requirements

- Python 3.12. The dependency versions and pre-trained model files are pinned for this runtime.
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
python3.12 -m venv .venv
source .venv/bin/activate
```

Install dependencies and start Streamlit:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m streamlit run app.py
```

## Deploy on Streamlit Community Cloud

Push the project to a GitHub repository, then create a Community Cloud app using that repository, the branch to deploy, and `app.py` as the entrypoint. In **Advanced settings**, select Python 3.12 to match the checked-in model and pinned dependencies. The app does not require Streamlit secrets: cover image URLs come from the dataset and no external API is called.

The pre-trained inference files under `artifacts/` are included, so the app can recommend books without downloading the full training dataset. Community Cloud installs the pinned dependencies from the root `requirements.txt`.

## Run with Docker

Install and start Docker Desktop (Windows or macOS) or the Docker Engine (Linux), then run these commands from the repository root:

```bash
docker build -t book-recommender .
docker run --name book-recommender -p 8501:8501 -v book-recommender-logs:/app/logs book-recommender
```

Open `http://localhost:8501` in a browser. The checked-in model is ready to use. The container needs internet access only if you choose to retrain. The named Docker volume keeps logs when the container is removed or replaced. The pre-trained inference files are included in each image build.

To stop the running container, press `Ctrl+C` in its terminal, or run `docker stop book-recommender` in another terminal. To start the existing stopped container again, use `docker start -ai book-recommender`.

The image uses Python 3.12 and contains the app code, configuration, dependencies, title list, and compact inference artifacts. `.dockerignore` excludes local environments, secrets, logs, notebooks, archives, raw datasets, and training intermediates from the build context. If you retrain inside a container, those new files remain in that container; rebuilding from the repository restores the checked-in pre-trained files.

## Train or refresh the recommender

The checked-in model is ready to use. To regenerate it, open **Training options** in the app and select **Train or refresh the recommender**. Training downloads the dataset, processes it, and fits a new model. It can take several minutes and needs enough memory and disk space. The app waits synchronously while training runs.

For regular Streamlit Community Cloud use, keep the checked-in model and avoid retraining in the hosted app. Retrain locally when you want to update the model or data.

The pipeline can also be started from the repository root in a Python environment with the requirements installed:

```bash
python -c "from books_recommender_system.pipeline.training_pipeline import TrainingPipeline; TrainingPipeline().start_training_pipeline()"
```

The command above runs ingestion, validation, transformation, and model training in order. It also needs network access to download the dataset.

## Use the application

1. Start Streamlit from the repository root.
2. Choose a title from the dropdown or type to filter the list.
3. Click **Show Recommendation**.
4. The application displays up to five similar titles and their available cover images.

The selection list is loaded from `templates/book_names.pkl`. If an inference artifact is missing, use the training option to regenerate the model files.

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

The repository includes the three files required for inference. Running the training pipeline also produces these additional local outputs under `artifacts/`:

```text
artifacts/
├── dataset/
│   ├── raw_data/books_data.zip
│   ├── ingested_data/                       # Extracted CSV files
│   ├── clean_data/clean_data.csv
│   └── transformed_data/transformed_data.pkl
├── serialized_objects/
│   ├── book_names.pkl                      # Generated by training, selection list is in templates/
│   ├── book_pivot.pkl                      # Tracked: needed for inference
│   └── final_rating.pkl                     # Tracked: needed for cover lookups
└── trained_model/model.pkl                  # Tracked: pre-trained inference model
```

The raw dataset, cleaned data, intermediate pivot, generated title list, and logs are ignored by Git. Re-running training recreates them. Do not load pickle files from sources you do not trust; Python pickle files can execute code when loaded.

## Configuration

Edit `config/config.yaml` to change the dataset URL or output directory names. The configuration is read when the application and pipeline components are initialized. The current app expects to be launched with the repository root as its working directory, so relative paths in the configuration resolve correctly.

Poster images are read directly from the dataset's `Image-URL-L` column. The app does not need an API key or Streamlit secrets.

## Troubleshooting

### “The recommender files are missing”

The app needs `artifacts/trained_model/model.pkl`, `artifacts/serialized_objects/book_pivot.pkl`, and `artifacts/serialized_objects/final_rating.pkl`. These inference files are included in this repository. If you removed them or they are missing, use **Training options** in the app to regenerate them.

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

- Keep downloaded datasets, intermediate training outputs, virtual environments, logs, and credentials out of source commits. The compact model and inference data files under `artifacts/` are tracked because the deployed app needs them.
- `books_data.zip`, `.env`, virtual environments, notebook data and outputs, training datasets, Python caches, and logs are ignored by `.gitignore`.
- If you choose to commit the dataset, check its redistribution terms and GitHub's file-size limits first. Large files may need Git Large File Storage.
- Dependencies are listed in `requirements.txt` and in `setup.py`. When changing runtime imports, update the dependency lists as needed.
- The Docker build context includes the compact inference artifacts and excludes local raw data and training intermediates. A log volume is configured by the example `docker run` command.
