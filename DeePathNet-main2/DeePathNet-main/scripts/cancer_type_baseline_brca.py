"""
Script to run baseline models for breast cancer subtype classification using cross validation
E.g. python cancer_type_baseline_brca.py
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import KFold
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from tqdm import tqdm
from xgboost import XGBClassifier

NUM_REPATE = 5
num_fold = 5

seed = 1


def run_model(input_df, clf_name, data_type=("mutation", "cnv", "rna")):
    count = 0
    clf_results_df = []
    if data_type[0] != "DR":
        input_df = input_df[
            [
                x
                for x in input_df.columns
                if (x.split("_")[1] in data_type) or (x.split("_")[0] in data_type)
            ]
        ]
    num_of_features = input_df.shape[1]
    cell_lines_all = input_df.index.values
    for n in range(NUM_REPATE):
        cv = KFold(n_splits=num_fold, shuffle=True, random_state=(seed + n))

        for cell_lines_train_index, cell_lines_val_index in tqdm(
            cv.split(cell_lines_all), total=num_fold
        ):
            train_lines = np.array(cell_lines_all)[cell_lines_train_index]
            val_lines = np.array(cell_lines_all)[cell_lines_val_index]

            merged_df_train = pd.merge(
                input_df[input_df.index.isin(train_lines)], target_df, on=["Cell_line"]
            )

            val_data = input_df[input_df.index.isin(val_lines)]

            merged_df_val = pd.merge(val_data, target_df, on=["Cell_line"])
            if clf_name == "RF":
                clf = RandomForestClassifier(n_jobs=40, max_features="sqrt")
            elif clf_name == "XGB":
                clf = XGBClassifier()
            elif clf_name == "LR":
                clf = LogisticRegression(n_jobs=40, solver="saga")
            elif clf_name == "ridge":
                clf = RidgeClassifier()
            elif clf_name == "KNN":
                clf = KNeighborsClassifier()
            elif clf_name == "SVML":
                clf = SVC(probability=True, kernel="linear")
            elif clf_name == "SVM":
                clf = SVC(probability=True, kernel="linear")
            elif clf_name == "NB":
                clf = GaussianNB()
            elif clf_name == "DT":
                clf = DecisionTreeClassifier()
            else:
                raise Exception
            clf.fit(
                merged_df_train.iloc[:, :num_of_features],
                merged_df_train.iloc[:, num_of_features:].values.flatten(),
            )
            y_pred = clf.predict(merged_df_val.iloc[:, :num_of_features])
            y_conf = clf.predict_proba(merged_df_val.iloc[:, :num_of_features])
            y_true = merged_df_val.iloc[:, num_of_features:].values.flatten()
            acc = accuracy_score(y_true, y_pred)
            f1 = f1_score(y_true, y_pred, average="macro")
            auc = roc_auc_score(y_true, y_conf, multi_class="ovo")
            clf_results_df.append(
                {"run": f"cv_{count}", "acc": acc, "f1": f1, "roc_auc": auc}
            )

            count += 1
    clf_results_df = pd.DataFrame(clf_results_df)
    return clf_results_df


input_df = pd.read_csv(
    "../data/processed/omics/tcga_brca_mutation_cnv_rna_log2.csv.gz", index_col=0
)

genes = np.unique(
    ([x.split("_")[0] for x in input_df.columns if x.split("_")[0] != "tissue"])
)

# target_df = pd.read_csv(
#     "../data/processed/cancer_type/tcga_23_cancer_types_mutation_cnv_rna.csv",
#     index_col=0)
target_df = pd.read_csv(
    "../data/processed/cancer_type/tcga_brca_mutation_cnv_rna_subtypes.csv", index_col=0
)


pathway_dict = {}
pathway_df = pd.read_csv(
    "../data/graph_predefined/LCPathways/41568_2020_240_MOESM4_ESM.csv"
)

pathway_df["genes"] = pathway_df["genes"].map(
    lambda x: "|".join([gene for gene in x.split("|") if gene in genes])
)
# pathway_df = pathway_df[pathway_df['Cancer_Publications'] > 50]

for index, row in pathway_df.iterrows():
    if row["genes"]:
        pathway_dict[row["name"]] = row["genes"].split("|")

cancer_genes = list(set([y for x in pathway_df["genes"].values for y in x.split("|")]))
non_cancer_genes = sorted(set(genes) - set(cancer_genes))

class_name_to_id = dict(
    zip(
        sorted(target_df.iloc[:, 0].unique()),
        list(range(target_df.iloc[:, 0].unique().size)),
    )
)
id_to_class_name = dict(
    zip(
        list(range(target_df.iloc[:, 0].unique().size)),
        sorted(target_df.iloc[:, 0].unique()),
    )
)

input_df_cancergenes = input_df[
    [x for x in input_df.columns if (x.split("_")[0] in cancer_genes)]
]

input_df_cancergenes = input_df_cancergenes.fillna(0)
input_df = input_df.fillna(0)
num_fold = 5

NUM_REPATE = 5

seed = 1

# %% BRCA
# print("Running LR")
# lr_results_df = run_model(input_df, "LR")
# lr_results_df.to_csv(
#     "../results/tcga_brca_subtype/lr_mutation_cnv_rna_allgenes.csv", index=False
# )
# print("Running RF")
# rf_results_df = run_model(input_df, "RF")
# rf_results_df.to_csv(
#     "../results/tcga_brca_subtype/rf_mutation_cnv_rna_allgenes.csv", index=False
# )
# print("Running KNN")
# knn_results_df = run_model(input_df, "KNN")
# knn_results_df.to_csv(
#     "../results/tcga_brca_subtype/knn_mutation_cnv_rna_allgenes.csv", index=False
# )
# print("Running DR")
# dt_results_df = run_model(input_df, "DT")
# dt_results_df.to_csv(
#     "../results/tcga_brca_subtype/dt_mutation_cnv_rna_allgenes.csv", index=False
# )
# print("Running PCA")
# pca_input_df = pd.read_csv(
#     "../data/DR/pca/tcga_brca_mutation_cnv_rna_allgenes.csv", index_col=0
# )
# rf_pca_results_df = run_model(pca_input_df, "RF", data_type=["DR"])
# rf_pca_results_df.to_csv(
#     "../results/tcga_brca_subtype/pca_rf_mutation_cnv_rna_allgenes.csv", index=False
# )
# print("Running moCluster")
# moCluster_input_df = pd.read_csv(
#     "../data/DR/moCluster/tcga_brca_mutation_cnv_rna.csv", index_col=0
# )
# moCluster_results_df = run_model(moCluster_input_df, "RF", data_type=["DR"])
# moCluster_results_df.to_csv(
#     "../results/tcga_brca_subtype/moCluster_rf_mutation_cnv_rna_allgenes.csv",
#     index=False,
# )

print("Running MOVE")
MOVE_input_df = pd.read_csv(
    "../data/DR/MOVE/tcga_brca_mutation_cnv_rna_200factor.csv", index_col=0
)
MOVE_results_df = run_model(MOVE_input_df, "RF", data_type=["DR"])
MOVE_results_df.to_csv(
    "../results/tcga_brca_subtype/MOVE_rf_mutation_cnv_rna_allgenes.csv", index=False
)

print("Running scVAEIT")
scVAEIT_input_df = pd.read_csv(
    "../data/DR/scVAEIT/tcga_brca_scvaeit_latent_200factor.csv", index_col=0
)
scVAEIT_results_df = run_model(scVAEIT_input_df, "RF", data_type=["DR"])
scVAEIT_results_df.to_csv(
    "../results/tcga_brca_subtype/scVAEIT_rf_mutation_cnv_rna_allgenes.csv", index=False
)
