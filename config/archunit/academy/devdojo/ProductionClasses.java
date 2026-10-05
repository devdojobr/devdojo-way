package academy.devdojo;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;

/** Production classes under the base package, imported once for all architecture rules. */
final class ProductionClasses {

    static final String BASE_PACKAGE = "academy.devdojo";

    static final JavaClasses CLASSES = new ClassFileImporter()
            .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
            .importPackages(BASE_PACKAGE);

    private ProductionClasses() {}
}
