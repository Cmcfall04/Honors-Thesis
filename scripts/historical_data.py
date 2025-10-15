import kagglehub

# Download latest version of the dataset
path = kagglehub.dataset_download("miguelaenlle/massive-stock-news-analysis-db-for-nlpbacktests")

print("Path to dataset files:", path)
