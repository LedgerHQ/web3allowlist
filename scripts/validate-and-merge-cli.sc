// Description: Validate and merge the CLI
// GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
//> using repository "https://NOBODY:{{ GITHUB_TOKEN }}@maven.pkg.github.com/LedgerHQ/_"
//> using lib "io.circe::circe-generic:0.14.3"
//> using lib "io.circe::circe-parser:0.14.3"
//> using lib "com.lihaoyi::os-lib:0.9.0"
//> using lib "co.ledger::tracing-commons:2.0.0"

import os.*

println(os.pwd)
