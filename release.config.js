var dryRun = (process.env.RELEASE_DRY_RUN || "false").toLowerCase() === "true";
var dockerhub_username = process.env.DOCKER_HUB_USERNAME;
var dockerhub_password = process.env.DOCKER_HUB_PASSWORD;

var prepareCmd = `echo "${dockerhub_password}" | docker login --username "${dockerhub_username}" --password-stdin`;
var publishCmd = "make publish PLUGIN_TAG=\${nextRelease.version}"

if (dryRun) {
    publishCmd = publishCmd.replace(" publish ", " build ");
}

var config = require('semantic-release-preconfigured-conventional-commits');

config.plugins.push(
    ["@semantic-release/exec", {
        "prepareCmd" : prepareCmd,
        "publishCmd": publishCmd,
    }]
)

if (!dryRun) {
    config.plugins.push(
        ["@semantic-release/github", {
            "assets": [
                { "path": "dist/*" },
            ]
        }],
        ["@semantic-release/git", {
            "assets": [
                "CHANGELOG.md",
            ],
            "message": "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}"
        }]
    );
}

module.exports = config