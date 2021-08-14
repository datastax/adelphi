import express from "express";
import _ from "lodash";
import { readDataFile } from "../utils";

/*
  Extracts key metrics of the Gemini results.
*/
function geminiSummary(gemini) {
  return _.isEmpty(gemini) ? {} : {
      write_ops: gemini.result.write_ops,
      write_errors: gemini.result.write_errors,
      read_ops: gemini.result.read_ops,
      read_errors: gemini.result.read_errors
    };
}

/*
  Extracts key metrics of the cass-diff results.
*/
function cassDiffSummary(cassdiff) {
  return _.isEmpty(cassdiff) ? {} : {
      matched_partitions: cassdiff.matched_partitions,
      matched_rows: cassdiff.matched_rows,
      matched_values: cassdiff.matched_values,
      mismatched_partitions: cassdiff.mismatched_partitions,
      mismatched_values: cassdiff.mismatched_values,
      partitions_only_in_source: cassdiff.partitions_only_in_source,
      partitions_only_in_target: cassdiff.partitions_only_in_target
    };
}

/*
  Returns the count of all errors in the results.
*/
function checkErrors(results) {
  return results.gemini.write_errors +
         results.gemini.read_errors +
         results.cassandra_diff.mismatched_partitions +
         results.cassandra_diff.mismatched_values;
}

/*
  Returns key metrics of the
  generated results files.
*/
export function resultsSummary(req, res) {
  console.log("GET /api/results/summary");
  /* Base path for the results file */
  const DATA_PATH = process.env.DATA_PATH;
  console.log("Data path: " + DATA_PATH);

  const result = {
    gemini: geminiSummary(readDataFile(DATA_PATH + "/gemini/results.json")),
    cassandra_diff: cassDiffSummary(readDataFile(DATA_PATH + "/cassandra-diff/job_results.json"))
  };
  
  const errorCount = checkErrors(result);
  const code = errorCount > 0 ? 500 : 200;
  res.status(code).send(result);
}

var app = express();

app.get('/results/summary', resultsSummary);

export default app;