import { ApiCheck, AssertionBuilder, CheckGroup } from "checkly/constructs";

// The agent resolves the compose service name; override for a deployed API.
const baseUrl = (process.env.MONITOR_TARGET_URL ?? "http://api:8000").replace(/\/$/, "");

const group = new CheckGroup("owl-fs-api-group", {
  name: "OWL Funds API",
  tags: ["owl-fs", "api"],
  // Alert channels are added in the Checkly dashboard for this POC; they can be
  // pulled in here as constructs later.
});

const defaults = {
  group,
  degradedResponseTime: 2000,
  maxResponseTime: 10000,
};

new ApiCheck("owl-health", {
  name: "GET /health",
  ...defaults,
  request: {
    method: "GET",
    url: `${baseUrl}/health`,
    assertions: [
      AssertionBuilder.statusCode().equals(200),
      AssertionBuilder.jsonBody("$.status").equals("ok"),
      AssertionBuilder.responseTime().lessThan(2000),
    ],
  },
});

new ApiCheck("owl-funds-list", {
  name: "GET /funds",
  ...defaults,
  request: {
    method: "GET",
    url: `${baseUrl}/funds`,
    queryParameters: [{ key: "limit", value: "5" }],
    assertions: [
      AssertionBuilder.statusCode().equals(200),
      AssertionBuilder.jsonBody("$.total").greaterThan(0),
      AssertionBuilder.jsonBody("$.funds").notEmpty(),
    ],
  },
});

new ApiCheck("owl-funds-filter", {
  name: "GET /funds?strategy=Infrastructure",
  ...defaults,
  request: {
    method: "GET",
    url: `${baseUrl}/funds`,
    queryParameters: [
      { key: "strategy", value: "Infrastructure" },
      { key: "limit", value: "3" },
    ],
    assertions: [
      AssertionBuilder.statusCode().equals(200),
      AssertionBuilder.jsonBody("$.funds[0].strategy").equals("Infrastructure"),
    ],
  },
});

new ApiCheck("owl-fund-detail", {
  name: "GET /funds/F-1001",
  ...defaults,
  request: {
    method: "GET",
    url: `${baseUrl}/funds/F-1001`,
    assertions: [
      AssertionBuilder.statusCode().equals(200),
      AssertionBuilder.jsonBody("$.fund_id").equals("F-1001"),
    ],
  },
});

new ApiCheck("owl-fund-missing", {
  name: "GET /funds/<unknown> -> 404",
  ...defaults,
  // A >= 400 response is the expected outcome here, so invert the pass/fail;
  // the assertion still pins it to exactly 404.
  shouldFail: true,
  request: {
    method: "GET",
    url: `${baseUrl}/funds/does-not-exist`,
    assertions: [AssertionBuilder.statusCode().equals(404)],
  },
});

new ApiCheck("owl-strategies", {
  name: "GET /strategies",
  ...defaults,
  request: {
    method: "GET",
    url: `${baseUrl}/strategies`,
    assertions: [
      AssertionBuilder.statusCode().equals(200),
      AssertionBuilder.jsonBody("$.strategies").notEmpty(),
    ],
  },
});
