package academy.devdojo;

import static academy.devdojo.ProductionClasses.CLASSES;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noFields;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noMethods;
import static com.tngtech.archunit.library.GeneralCodingRules.NO_CLASSES_SHOULD_ACCESS_STANDARD_STREAMS;
import static com.tngtech.archunit.library.GeneralCodingRules.NO_CLASSES_SHOULD_THROW_GENERIC_EXCEPTIONS;

import org.junit.jupiter.api.Test;

/** Coding rules that apply to every production class. */
class CodingRulesTest {

    private static final String AUTOWIRED = "org.springframework.beans.factory.annotation.Autowired";
    private static final String VALUE = "org.springframework.beans.factory.annotation.Value";
    private static final String JAKARTA_INJECT = "jakarta.inject.Inject";
    private static final String JAKARTA_RESOURCE = "jakarta.annotation.Resource";
    private static final String CONSTRUCTOR_INJECTION =
            "dependencies must be injected through the constructor: declare a private final field and a constructor"
                    + " parameter (configuration values: @Value on the constructor parameter or"
                    + " a @ConfigurationProperties record)";

    @Test
    void onlyConstructorInjectionIsUsedForFields() {
        noFields()
                .should()
                .beAnnotatedWith(AUTOWIRED)
                .orShould()
                .beAnnotatedWith(VALUE)
                .orShould()
                .beAnnotatedWith(JAKARTA_INJECT)
                .orShould()
                .beAnnotatedWith(JAKARTA_RESOURCE)
                .because(CONSTRUCTOR_INJECTION)
                .allowEmptyShould(true)
                .check(CLASSES);
    }

    @Test
    void onlyConstructorInjectionIsUsedForMethods() {
        noMethods()
                .should()
                .beAnnotatedWith(AUTOWIRED)
                .orShould()
                .beAnnotatedWith(JAKARTA_INJECT)
                .orShould()
                .beAnnotatedWith(JAKARTA_RESOURCE)
                .because(CONSTRUCTOR_INJECTION)
                .allowEmptyShould(true)
                .check(CLASSES);
    }

    @Test
    void noGenericExceptionsAreThrown() {
        NO_CLASSES_SHOULD_THROW_GENERIC_EXCEPTIONS
                .because("throw a specific exception type that names the failure (e.g. EnrollmentNotFoundException)")
                .check(CLASSES);
    }

    @Test
    void noStandardStreamsAreUsed() {
        NO_CLASSES_SHOULD_ACCESS_STANDARD_STREAMS
                .because("use an SLF4J logger (org.slf4j.LoggerFactory.getLogger(...)) instead")
                .check(CLASSES);
    }
}
