import { config as loadEnv } from "dotenv";
import { defineConfig } from "checkly";
import { Frequency } from "checkly/constructs";

// Reuse the repo's root .env — the Checkly vars live alongside the app's.
// Absent in CI, where the values come from workflow env / repo secrets.
loadEnv({ path: "../.env" });

const privateLocation = process.env.CHECKLY_PRIVATE_LOCATION?.trim();

export default defineConfig({
  projectName: "OWL Funds API",
  logicalId: "owl-fs-api-monitoring",
  repoUrl: "https://github.com/kingvilceus/mtv-owl-fs-assessment",
  checks: {
    runtimeId: "2025.04",
    frequency: Frequency.EVERY_5M,
    checkMatch: "__checks__/**/*.check.ts",
    tags: ["owl-fs"],
    // With a private location the checks run on the in-cluster agent against
    // http://api:8000. Without one they run from Checkly's public locations and
    // need a publicly reachable MONITOR_TARGET_URL.
    ...(privateLocation
      ? { privateLocations: [privateLocation] }
      : { locations: ["us-east-1", "eu-west-1"] }),
  },
  cli: {
    reporters: ["list"],
  },
});
