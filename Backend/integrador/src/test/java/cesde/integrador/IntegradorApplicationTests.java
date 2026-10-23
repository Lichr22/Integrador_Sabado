package cesde.integrador;

import org.mockito.Mockito;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.jdbc.core.JdbcTemplate;

@SpringBootTest(properties = {
		"app.auth.token-secret=test-only-secret-with-more-than-32-bytes",
		"spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration,org.springframework.boot.autoconfigure.orm.jpa.HibernateJpaAutoConfiguration"
})
@Import(IntegradorApplicationTests.TestDependencies.class)
class IntegradorApplicationTests {

	@Test
	void contextLoads() {
	}

	@TestConfiguration
	static class TestDependencies {
		@Bean
		JdbcTemplate jdbcTemplate() {
			return Mockito.mock(JdbcTemplate.class);
		}
	}
}
