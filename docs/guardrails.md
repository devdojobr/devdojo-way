# Guardrails

Quality and architecture rules are enforced by tools, not by convention. `./mvnw verify` must pass before
any change is done. A failure message names the rule; fix the code, never the rule.

## Commands

| Purpose | Command |
|---|---|
| Full gate (CI runs exactly this) | `./mvnw verify` |
| Gate + mutation testing (slow) | `./mvnw verify -Pquality` |
| Auto-fix formatting | `./mvnw spotless:apply` |
| Auto-fix common violations, then reformat | `./mvnw rewrite:run && ./mvnw spotless:apply` |
| Check your change stays in your slice | `scripts/check-scope.sh <slice>` |

Always use `./mvnw` (Maven 3.10.0+, Java 25). The build needs Docker running (Testcontainers MySQL).

## Tools

Rows are in build order: the first failing gate stops the build.

| Tool | Enforces | Where the message is | Auto-fix |
|---|---|---|---|
| Maven Enforcer | Java 25+, Maven 3.10.0+, dependency convergence, no duplicate classes | `[ERROR] Rule ... failed` | — |
| javac `-Xlint:all -Werror` | every compiler warning is an error | the `[WARNING] File.java:[line,col] ...` lines **above** "warnings found and -Werror specified" | — |
| Error Prone | bug patterns at compile time | `[ERROR] File.java:[l,c] [CheckName] ...` + link + "Did you mean" | apply the suggestion |
| NullAway (JSpecify) | null safety in `src/main/java`; everything is non-null unless `@Nullable` | `[ERROR] ... [NullAway] ...` | — |
| ArchUnit (`config/archunit`) | slice structure, constructor injection, no generic exceptions, no `System.out/err`, naming, `@NullMarked` packages | test failure `Architecture Violation ... Rule '...' was violated` | — |
| Spring Modulith (`ModularityTest`) | no cycles between slices, no access to another slice's sub-packages, only declared `allowedDependencies` | test failure `org.springframework.modulith.core.Violations` | — |
| Spotless (palantir-java-format) | formatting, unused/wildcard imports | `[ERROR] ... format violations` with a diff | `./mvnw spotless:apply` |
| JaCoCo | line coverage ≥ 80% (`DevdojoWayApplication` excluded) | `[WARNING] Rule violated for bundle ...: lines covered ratio is X` | write tests; report in `target/site/jacoco/index.html` |
| Checkstyle | naming; main code: file ≤ 300 lines, method ≤ 30 lines, ≤ 5 parameters (incl. constructors), ≤ 8 record components; all code: no suppressions; tests: no `@Disabled*` | `[ERROR] File.java:line: message [CheckName]` | — |
| PMD | cyclomatic complexity ≤ 10, cognitive complexity ≤ 15, coupling, god class, Law of Demeter, unused code (main code) | `[WARNING] PMD Failure: Class:line Rule:Name ...` | `rewrite:run` fixes some unused code |
| CPD | duplicated blocks ≥ 100 tokens (main code) | `[WARNING] CPD Failure: Found N lines ... at locations:` | extract the shared code |
| SpotBugs + FindSecBugs | bug patterns and security issues in bytecode (main code) | `[ERROR] High/Medium: ... PATTERN_NAME` | — |
| dependency:analyze | no used-but-undeclared or declared-but-unused dependencies | `[ERROR] Used undeclared dependencies found:` | ask a human (see below) |
| PIT (`-Pquality`) | mutation score ≥ 70% | `Mutation score of X is below threshold of 70`; report in `target/pit-reports/index.html` | add assertions that fail when behaviour changes |
| OpenRewrite | not a gate: recipes in `config/rewrite/rewrite.yml` | — | `./mvnw rewrite:run` |

## Rules that cannot be bypassed

- No `@SuppressWarnings`, `@SuppressFBWarnings`, `// NOPMD`, `// NOSONAR`, `// CHECKSTYLE:OFF`, or `@Disabled` tests.
- Skip and ignore flags (`-DskipTests`, `-Dcheckstyle.skip`, `-Dpmd.skip`, `-Djacoco.skip`,
  `-Dmaven.test.failure.ignore`, ...) are hard-coded off in `pom.xml` and have no effect.
- `config/`, `pom.xml`, `.mvn/`, `scripts/`, `.github/` and this file are human-owned. `scripts/check-scope.sh`
  fails if you change them. If a rule seems wrong, or you need a dependency that is not declared, stop and ask.

## Architecture: vertical slices

- Every top-level package under `academy.devdojo` is a feature slice and a Spring Modulith module.
  Only `DevdojoWayApplication` lives in `academy.devdojo` itself.
- The slice's base package (`academy.devdojo.<slice>`) is its public API. Sub-packages are internal.
  `@NamedInterface` and `@ApplicationModule(type = OPEN)` are forbidden.
- Slices talk to each other only through public API types or application events, and only to slices listed
  in `allowedDependencies`. No cycles between slices, and no cycles between sub-packages of one slice.
- Forbidden top-level names: `controller(s)`, `service(s)`, `repository`/`repositories`, `dto(s)`, `model(s)`,
  `entity`/`entities`, `domain`, `util(s)`, `helper(s)`, `common`, `shared`, `core`, `config`, `configuration`,
  `infra`, `infrastructure`, `api`, `web`, `persistence`, `exception(s)`.
- Naming (both directions): `@Controller`/`@RestController` ⇔ `*Controller`; Spring Data repository or
  `@Repository` ⇔ `*Repository`; `@Configuration` ⇔ `*Configuration`; `@ConfigurationProperties` ⇔ `*Properties`.
- Inject only through constructors. No `@Autowired`/`@Inject`/`@Resource`/`@Value` on fields or methods.
- Throw specific exceptions, not `Exception`, `RuntimeException` or `Throwable`. Log with SLF4J, not `System.out`.

## Adding a slice

1. Pick a business-capability name (`enrollment`, `mentoring`), not a technical one.
2. Create `src/main/java/academy/devdojo/<slice>/package-info.java`:

   ```java
   @ApplicationModule(allowedDependencies = {})   // list slices you use, e.g. {"track"}
   @NullMarked
   package academy.devdojo.<slice>;

   import org.jspecify.annotations.NullMarked;
   import org.springframework.modulith.ApplicationModule;
   ```

3. Every sub-package needs its own `package-info.java` with `@NullMarked`.
4. Put files only in these paths:
   - `src/main/java/academy/devdojo/<slice>/`
   - `src/test/java/academy/devdojo/<slice>/`
   - `src/main/resources/<slice>/`
   - `src/test/resources/<slice>/`
   - `src/main/resources/db/migration/<slice>/`
5. Name Flyway migrations with a timestamp version so slices never collide:
   `V<yyyyMMddHHmm>__<slice>_<description>.sql`.
6. Run `./mvnw verify` and `scripts/check-scope.sh <slice>`.

## Dependencies available without a pom change

These are pre-declared and may be imported directly. Anything else needs a human to edit `pom.xml`:
`spring-core`, `spring-context`, `spring-beans`, `spring-web`, `spring-webmvc`, `spring-tx`, `spring-boot`,
`spring-boot-autoconfigure`, `spring-data-jpa`, `spring-data-commons`, `jakarta.persistence-api`,
`spring-security-core`, `spring-security-web`, `spring-security-config`, `spring-modulith-api`, `jspecify`, `slf4j-api`,
`jackson-databind` (Jackson 3, `tools.jackson`).

Tests also get: `junit-jupiter-api`, `assertj-core`, `mockito-core`, `spring-test`, `spring-boot-test`,
`spring-boot-webmvc-test`, `spring-boot-data-jpa-test`, `spring-security-test`, `testcontainers`,
`spring-modulith-test`, `spring-modulith-core`, `archunit`.
