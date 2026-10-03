"""I clean PIR data, create five-minute summaries, and make analysis files."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import binomtest


WINDOW_MINUTES = 5
SAMPLE_SECONDS = 5


def read_arguments():
    parser = argparse.ArgumentParser(description="Analyse PIR data for SIT225 4P.")
    parser.add_argument("--raw", default="raw_pir_data.csv", help="Raw PIR CSV file")
    parser.add_argument(
        "--log", default="collection_log.csv", help="Completed 25-window collection log"
    )
    parser.add_argument("--output-folder", default="analysis_output", help="Output folder")
    return parser.parse_args()


def make_label(motion_samples, total_samples):
    if total_samples == 0:
        return ""
    if motion_samples == 0:
        return "no motion detected"
    if motion_samples == 1:
        return "unclear"
    return "motion detected"


def save_time_series(raw_data, output_path):
    plt.figure(figsize=(11, 4.5))
    plt.step(raw_data["timestamp"], raw_data["pir_reading"], where="post", color="#1f77b4")
    plt.yticks([0, 1], ["No motion", "Motion"])
    plt.xlabel("Time")
    plt.ylabel("PIR reading")
    plt.title("My PIR Readings Over Time")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def save_histogram(summary, output_path):
    plt.figure(figsize=(8, 4.5))
    plt.hist(summary["motion_samples"], bins=10, color="#2a9d8f", edgecolor="black")
    plt.xlabel("Motion samples in one five-minute window")
    plt.ylabel("Number of windows")
    plt.title("My Distribution of PIR Motion Samples")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def save_condition_boxplot(summary, output_path):
    condition_order = [
        "Normal desk work",
        "Quiet sitting",
        "Empty desk",
        "Walking past desk",
        "Movement near door",
    ]
    groups = [
        summary.loc[summary["condition"] == condition, "motion_samples"].dropna()
        for condition in condition_order
    ]
    plt.figure(figsize=(10, 5))
    plt.boxplot(groups, tick_labels=condition_order, showmeans=True)
    plt.xticks(rotation=20, ha="right")
    plt.xlabel("Test condition")
    plt.ylabel("Motion samples in one five-minute window")
    plt.title("My PIR Motion Samples by Test Condition")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def save_relationship_plot(summary, output_path):
    comparison = summary[summary["condition"].isin(["Normal desk work", "Empty desk"])].copy()
    comparison["reference_desk_motion"] = (
        comparison["condition"] == "Normal desk work"
    ).astype(int)
    jitter = np.linspace(-0.04, 0.04, len(comparison))

    plt.figure(figsize=(7, 5))
    colours = np.where(comparison["reference_desk_motion"] == 1, "#e76f51", "#457b9d")
    plt.scatter(
        comparison["reference_desk_motion"] + jitter,
        comparison["motion_samples"],
        c=colours,
        s=70,
    )
    plt.xticks([0, 1], ["Empty desk", "Normal desk work"])
    plt.xlabel("Reference test condition")
    plt.ylabel("Motion samples in one five-minute window")
    plt.title("My PIR Motion and Reference Desk Movement")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def one_sided_binomial_result(summary, condition, expected_label):
    rows = summary[(summary["condition"] == condition) & (summary["final_label"] != "")]
    total = len(rows)
    successes = int((rows["final_label"] == expected_label).sum())

    if total == 0:
        return successes, total, "not available"

    result = binomtest(successes, total, p=0.5, alternative="greater")
    return successes, total, f"{result.pvalue:.4f}"


def main():
    args = read_arguments()
    output_folder = Path(args.output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    raw = pd.read_csv(args.raw)
    raw_rows_before_cleaning = len(raw)
    raw["timestamp"] = pd.to_datetime(raw["timestamp"], errors="coerce")
    raw["pir_reading"] = pd.to_numeric(raw["pir_reading"], errors="coerce")

    invalid_rows = raw[
        raw["timestamp"].isna() | ~raw["pir_reading"].isin([0, 1])
    ].copy()
    clean = raw.drop(index=invalid_rows.index).copy()
    duplicate_count = int(clean.duplicated(subset=["timestamp"]).sum())
    clean = clean.drop_duplicates(subset=["timestamp"], keep="first").sort_values("timestamp")
    clean["pir_reading"] = clean["pir_reading"].astype(int)

    if clean.empty:
        raise ValueError("No valid 0 or 1 readings were found in the raw CSV.")

    log = pd.read_csv(args.log)
    if len(log) != 25:
        raise ValueError("The collection log must contain exactly 25 planned windows.")
    required_log_columns = ["condition", "actual_start_time", "actual_end_time"]
    missing_log_columns = [column for column in required_log_columns if column not in log.columns]
    if missing_log_columns:
        raise ValueError(
            "The collection log is missing: " + ", ".join(missing_log_columns)
        )

    log["actual_start_time"] = pd.to_datetime(log["actual_start_time"], errors="coerce")
    log["actual_end_time"] = pd.to_datetime(log["actual_end_time"], errors="coerce")
    if log[["actual_start_time", "actual_end_time"]].isna().any().any():
        raise ValueError("Enter an actual start time and end time for every window.")
    if (log["actual_end_time"] <= log["actual_start_time"]).any():
        raise ValueError("Each actual end time must be later than its start time.")

    summaries = []
    for index, log_row in log.iterrows():
        window_number = index + 1
        window_start = log_row["actual_start_time"]
        window_end = log_row["actual_end_time"]
        window_data = clean[(clean["timestamp"] >= window_start) & (clean["timestamp"] < window_end)]
        total_samples = len(window_data)
        motion_samples = int(window_data["pir_reading"].sum())

        summaries.append(
            {
                "window_number": window_number,
                "round_number": log_row.get("round_number", ""),
                "window_start": window_start.isoformat(sep=" ", timespec="seconds"),
                "window_end": window_end.isoformat(sep=" ", timespec="seconds"),
                "condition": log_row["condition"],
                "expected_desk_motion": log_row.get("expected_desk_motion", ""),
                "total_samples": total_samples,
                "motion_samples": motion_samples,
                "motion_percent": round((motion_samples / total_samples) * 100, 2)
                if total_samples
                else np.nan,
                "final_label": make_label(motion_samples, total_samples),
                "sensor_position_and_angle": log_row.get("sensor_position_and_angle", ""),
                "other_people_present": log_row.get("other_people_present", ""),
                "notes": log_row.get("notes", ""),
            }
        )

    summary = pd.DataFrame(summaries)
    summary.to_csv(output_folder / "processed_pir_data.csv", index=False)

    stats = summary["motion_samples"].describe(percentiles=[0.25, 0.75, 0.95]).to_frame(
        name="motion_samples"
    )
    stats.loc["range", "motion_samples"] = (
        summary["motion_samples"].max() - summary["motion_samples"].min()
    )
    stats.to_csv(output_folder / "descriptive_statistics.csv")

    save_time_series(clean, output_folder / "plot_1_time_series.png")
    save_histogram(summary, output_folder / "plot_2_histogram.png")
    save_relationship_plot(summary, output_folder / "plot_3_relationship.png")
    save_condition_boxplot(summary, output_folder / "plot_4_boxplot.png")

    h1_successes, h1_total, h1_p_value = one_sided_binomial_result(
        summary, "Normal desk work", "motion detected"
    )
    h2_successes, h2_total, h2_p_value = one_sided_binomial_result(
        summary, "Empty desk", "no motion detected"
    )

    possible_false_positives = int(
        ((summary["expected_desk_motion"] == "no")
        & (summary["final_label"] == "motion detected")).sum()
    )
    possible_false_negatives = int(
        ((summary["expected_desk_motion"] == "yes")
        & (summary["final_label"] == "no motion detected")).sum()
    )

    expected_raw_rows = int(
        (clean["timestamp"].iloc[-1] - clean["timestamp"].iloc[0]).total_seconds()
        / SAMPLE_SECONDS
    ) + 1
    estimated_missing_rows = max(0, expected_raw_rows - len(clean))
    missing_percent = (
        (estimated_missing_rows / expected_raw_rows) * 100 if expected_raw_rows else 0
    )
    current_raw_reduction = (1 - (len(summary) / len(clean))) * 100
    one_second_baseline_rows = len(summary) * WINDOW_MINUTES * 60
    one_second_reduction = (1 - (len(summary) / one_second_baseline_rows)) * 100

    results = [
        "My SIT225 4P PIR Analysis Results",
        "",
        "My data quality check",
        f"I started with {raw_rows_before_cleaning} raw rows.",
        f"I removed {len(invalid_rows)} invalid rows.",
        f"I removed {duplicate_count} duplicate timestamps.",
        f"I finished with {len(clean)} raw rows.",
        f"I estimated {estimated_missing_rows} missing rows.",
        f"My estimated missing percentage was {missing_percent:.2f}%.",
        "",
        "My hypothesis tests",
        f"For H1, I found motion detected in {h1_successes}/{h1_total} normal desk-work windows.",
        f"My H1 one-sided exact binomial p-value was {h1_p_value}.",
        f"For H2, I found no motion detected in {h2_successes}/{h2_total} empty-desk windows.",
        f"My H2 one-sided exact binomial p-value was {h2_p_value}.",
        "",
        "My possible PIR errors",
        f"I found {possible_false_positives} possible unwanted motion alerts in no-motion conditions.",
        f"I found {possible_false_negatives} possible missed motion windows in normal desk work.",
        "I based these counts on my planned condition. They do not prove why a PIR reading occurred.",
        "",
        "My storage comparison",
        f"I reduced records by {current_raw_reduction:.2f}% when I changed five-second raw readings into five-minute summaries.",
        f"I reduced records by {one_second_reduction:.2f}% when I compared five-minute summaries with a one-second baseline.",
        "",
        "My interpretation rule",
        "I treated the PIR result as motion near my desk. I did not treat it as proof of study time, attendance, focus, or productivity.",
    ]
    (output_folder / "analysis_results.txt").write_text("\n".join(results), encoding="utf-8")

    print("Analysis finished.")
    print(f"Files saved in: {output_folder.resolve()}")


if __name__ == "__main__":
    main()
