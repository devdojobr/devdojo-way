package academy.devdojo;

import org.springframework.boot.SpringApplication;

public class TestDevdojoWayApplication {

	public static void main(String[] args) {
		SpringApplication.from(DevdojoWayApplication::main).with(TestcontainersConfiguration.class).run(args);
	}

}
