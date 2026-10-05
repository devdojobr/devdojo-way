package academy.devdojo;

import static academy.devdojo.ProductionClasses.BASE_PACKAGE;
import static academy.devdojo.ProductionClasses.CLASSES;
import static com.tngtech.archunit.lang.SimpleConditionEvent.violated;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.all;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;
import static com.tngtech.archunit.library.dependencies.SlicesRuleDefinition.slices;

import com.tngtech.archunit.core.domain.JavaAnnotation;
import com.tngtech.archunit.core.domain.JavaClass;
import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.domain.JavaEnumConstant;
import com.tngtech.archunit.core.domain.JavaPackage;
import com.tngtech.archunit.lang.AbstractClassesTransformer;
import com.tngtech.archunit.lang.ArchCondition;
import com.tngtech.archunit.lang.ClassesTransformer;
import com.tngtech.archunit.lang.ConditionEvents;
import java.util.Optional;
import java.util.Set;
import java.util.TreeMap;
import org.junit.jupiter.api.Test;

/** Vertical-slice structure: what may exist at the top level and how each slice declares itself. */
class SliceStructureRulesTest {

    private static final String APPLICATION_MODULE = "org.springframework.modulith.ApplicationModule";
    private static final String NAMED_INTERFACE = "org.springframework.modulith.NamedInterface";
    private static final String NULL_MARKED = "org.jspecify.annotations.NullMarked";
    private static final String SPRING_BOOT_APPLICATION =
            "org.springframework.boot.autoconfigure.SpringBootApplication";
    private static final String PACKAGE_INFO = "package-info";

    private static final Set<String> TECHNICAL_PACKAGE_NAMES = Set.of(
            "controller",
            "controllers",
            "service",
            "services",
            "repository",
            "repositories",
            "dto",
            "dtos",
            "model",
            "models",
            "entity",
            "entities",
            "domain",
            "util",
            "utils",
            "helper",
            "helpers",
            "common",
            "shared",
            "core",
            "config",
            "configuration",
            "infra",
            "infrastructure",
            "api",
            "web",
            "persistence",
            "exception",
            "exceptions");

    /** The top-level packages under the base package. Each one is a feature slice. */
    private static final ClassesTransformer<JavaPackage> FEATURE_SLICES =
            new AbstractClassesTransformer<>("feature slices (top-level packages under " + BASE_PACKAGE + ")") {
                @Override
                public Iterable<JavaPackage> doTransform(JavaClasses classes) {
                    return classes.containPackage(BASE_PACKAGE)
                            ? classes.getPackage(BASE_PACKAGE).getSubpackages()
                            : Set.of();
                }
            };

    /** Every package under the base package that contains at least one class. */
    private static final ClassesTransformer<JavaPackage> PACKAGES_WITH_CLASSES =
            new AbstractClassesTransformer<>("packages under " + BASE_PACKAGE) {
                @Override
                public Iterable<JavaPackage> doTransform(JavaClasses classes) {
                    var packages = new TreeMap<String, JavaPackage>();
                    for (JavaClass javaClass : classes) {
                        packages.putIfAbsent(javaClass.getPackageName(), javaClass.getPackage());
                    }
                    return packages.values();
                }
            };

    @Test
    void topLevelPackagesAreFeatureSlicesNotTechnicalLayers() {
        all(FEATURE_SLICES)
                .should(notBeNamedAfterATechnicalLayer())
                .allowEmptyShould(true)
                .check(CLASSES);
    }

    @Test
    void basePackageContainsOnlyTheApplicationClass() {
        classes()
                .that()
                .resideInAPackage(BASE_PACKAGE)
                .and()
                .doNotHaveSimpleName(PACKAGE_INFO)
                .should()
                .beAnnotatedWith(SPRING_BOOT_APPLICATION)
                .because("the base package is not a catch-all; move this class into the feature slice that owns it")
                .check(CLASSES);
    }

    @Test
    void everySliceDeclaresItsAllowedDependencies() {
        all(FEATURE_SLICES)
                .should(declareAllowedDependenciesExplicitly())
                .allowEmptyShould(true)
                .check(CLASSES);
    }

    @Test
    void slicesAreNotOpenModules() {
        all(FEATURE_SLICES).should(notBeOpenModules()).allowEmptyShould(true).check(CLASSES);
    }

    @Test
    void noNamedInterfacesExposeSliceInternals() {
        noClasses()
                .should()
                .beAnnotatedWith(NAMED_INTERFACE)
                .because("a slice's public API is its base package only; sub-packages are internal")
                .check(CLASSES);
        all(PACKAGES_WITH_CLASSES)
                .should(notBeAnnotatedWith(NAMED_INTERFACE))
                .allowEmptyShould(true)
                .check(CLASSES);
    }

    @Test
    void subPackagesInsideASliceAreFreeOfCycles() {
        slices().matching(BASE_PACKAGE + ".(*).(*)..")
                .namingSlices("slice '$1', sub-package '$2'")
                .should()
                .beFreeOfCycles()
                .allowEmptyShould(true)
                .check(CLASSES);
    }

    @Test
    void everyPackageIsNullMarked() {
        all(PACKAGES_WITH_CLASSES).should(beNullMarked()).check(CLASSES);
    }

    private static ArchCondition<JavaPackage> notBeNamedAfterATechnicalLayer() {
        return new ArchCondition<>("be named after a business capability, not a technical layer or catch-all") {
            @Override
            public void check(JavaPackage slice, ConditionEvents events) {
                if (TECHNICAL_PACKAGE_NAMES.contains(slice.getRelativeName())) {
                    events.add(violated(
                            slice,
                            "Top-level package " + slice.getName() + " is a technical-layer or catch-all name ('"
                                    + slice.getRelativeName() + "'). Every top-level package under " + BASE_PACKAGE
                                    + " must be a feature slice named after a business capability (e.g. "
                                    + BASE_PACKAGE + ".enrollment). Move its classes into the slice that owns them,"
                                    + " or into a narrowly scoped module with an explicit name."));
                }
            }
        };
    }

    private static ArchCondition<JavaPackage> declareAllowedDependenciesExplicitly() {
        return new ArchCondition<>("declare @ApplicationModule(allowedDependencies = ...) in package-info.java") {
            @Override
            public void check(JavaPackage slice, ConditionEvents events) {
                Optional<JavaAnnotation<JavaPackage>> module = slice.tryGetAnnotationOfType(APPLICATION_MODULE);
                if (module.isEmpty() || !module.get().hasExplicitlyDeclaredProperty("allowedDependencies")) {
                    events.add(violated(
                            slice,
                            "Slice " + slice.getName() + " does not declare its dependencies. Add to "
                                    + "src/main/java/" + slice.getName().replace('.', '/') + "/package-info.java: "
                                    + "@ApplicationModule(allowedDependencies = {}) listing every slice it uses, "
                                    + "e.g. {\"track\", \"mentoring\"}; use {} for none."));
                }
            }
        };
    }

    private static ArchCondition<JavaPackage> notBeOpenModules() {
        return new ArchCondition<>("not be declared @ApplicationModule(type = OPEN)") {
            @Override
            public void check(JavaPackage slice, ConditionEvents events) {
                boolean open = slice.tryGetAnnotationOfType(APPLICATION_MODULE)
                        .flatMap(module -> module.tryGetExplicitlyDeclaredProperty("type"))
                        .filter(type -> type instanceof JavaEnumConstant constant && "OPEN".equals(constant.name()))
                        .isPresent();
                if (open) {
                    events.add(violated(
                            slice,
                            "Slice " + slice.getName() + " is declared OPEN, which exposes its internal sub-packages "
                                    + "to other slices. Remove 'type = Type.OPEN' and depend only on public APIs."));
                }
            }
        };
    }

    private static ArchCondition<JavaPackage> notBeAnnotatedWith(String annotation) {
        return new ArchCondition<>("not be annotated with @" + annotation) {
            @Override
            public void check(JavaPackage javaPackage, ConditionEvents events) {
                if (javaPackage.isAnnotatedWith(annotation)) {
                    events.add(violated(
                            javaPackage,
                            "Package " + javaPackage.getName() + " is annotated with @" + annotation
                                    + ". Sub-packages are internal to their slice; expose types through the slice's"
                                    + " base package instead."));
                }
            }
        };
    }

    private static ArchCondition<JavaPackage> beNullMarked() {
        return new ArchCondition<>("be annotated with @NullMarked in package-info.java") {
            @Override
            public void check(JavaPackage javaPackage, ConditionEvents events) {
                if (!javaPackage.isAnnotatedWith(NULL_MARKED)) {
                    events.add(violated(
                            javaPackage,
                            "Package " + javaPackage.getName() + " is not @NullMarked. Create "
                                    + "src/main/java/" + javaPackage.getName().replace('.', '/') + "/package-info.java"
                                    + " containing: @NullMarked package " + javaPackage.getName()
                                    + "; import org.jspecify.annotations.NullMarked;"));
                }
            }
        };
    }
}
