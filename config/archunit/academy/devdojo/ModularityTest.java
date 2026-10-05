package academy.devdojo;

import org.junit.jupiter.api.Test;
import org.springframework.modulith.core.ApplicationModules;

/**
 * Spring Modulith verification: every top-level package under the base package is an application module (feature
 * slice). Fails on cycles between slices, access to another slice's internal sub-packages, and dependencies not listed
 * in the slice's {@code @ApplicationModule(allowedDependencies = ...)}.
 */
class ModularityTest {

    @Test
    void slicesRespectModuleBoundaries() {
        ApplicationModules.of(DevdojoWayApplication.class).verify();
    }
}
