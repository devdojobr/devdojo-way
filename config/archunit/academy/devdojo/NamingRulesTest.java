package academy.devdojo;

import static academy.devdojo.ProductionClasses.CLASSES;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes;

import org.junit.jupiter.api.Test;

/** Naming conventions, enforced in both directions: annotation implies suffix, suffix implies annotation. */
class NamingRulesTest {

    private static final String CONTROLLER = "org.springframework.stereotype.Controller";
    private static final String REPOSITORY = "org.springframework.stereotype.Repository";
    private static final String SPRING_DATA_REPOSITORY = "org.springframework.data.repository.Repository";
    private static final String CONFIGURATION = "org.springframework.context.annotation.Configuration";
    private static final String CONFIGURATION_PROPERTIES =
            "org.springframework.boot.context.properties.ConfigurationProperties";

    @Test
    void controllersAreNamedController() {
        classes()
                .that()
                .areMetaAnnotatedWith(CONTROLLER)
                .should()
                .haveSimpleNameEndingWith("Controller")
                .allowEmptyShould(true)
                .check(CLASSES);
        classes()
                .that()
                .haveSimpleNameEndingWith("Controller")
                .should()
                .beMetaAnnotatedWith(CONTROLLER)
                .because("only @Controller/@RestController classes may be named *Controller")
                .allowEmptyShould(true)
                .check(CLASSES);
    }

    @Test
    void repositoriesAreNamedRepository() {
        classes()
                .that()
                .areAssignableTo(SPRING_DATA_REPOSITORY)
                .or()
                .areAnnotatedWith(REPOSITORY)
                .should()
                .haveSimpleNameEndingWith("Repository")
                .allowEmptyShould(true)
                .check(CLASSES);
        classes()
                .that()
                .haveSimpleNameEndingWith("Repository")
                .should()
                .beAssignableTo(SPRING_DATA_REPOSITORY)
                .orShould()
                .beAnnotatedWith(REPOSITORY)
                .because("only Spring Data repositories and @Repository classes may be named *Repository")
                .allowEmptyShould(true)
                .check(CLASSES);
    }

    @Test
    void configurationClassesAreNamedConfiguration() {
        classes()
                .that()
                .areAnnotatedWith(CONFIGURATION)
                .should()
                .haveSimpleNameEndingWith("Configuration")
                .allowEmptyShould(true)
                .check(CLASSES);
        classes()
                .that()
                .haveSimpleNameEndingWith("Configuration")
                .should()
                .beMetaAnnotatedWith(CONFIGURATION)
                .because("only @Configuration classes may be named *Configuration")
                .allowEmptyShould(true)
                .check(CLASSES);
    }

    @Test
    void configurationPropertiesAreNamedProperties() {
        classes()
                .that()
                .areAnnotatedWith(CONFIGURATION_PROPERTIES)
                .should()
                .haveSimpleNameEndingWith("Properties")
                .allowEmptyShould(true)
                .check(CLASSES);
        classes()
                .that()
                .haveSimpleNameEndingWith("Properties")
                .should()
                .beAnnotatedWith(CONFIGURATION_PROPERTIES)
                .because("only @ConfigurationProperties classes may be named *Properties")
                .allowEmptyShould(true)
                .check(CLASSES);
    }
}
