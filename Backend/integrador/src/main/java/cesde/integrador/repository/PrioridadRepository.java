package cesde.integrador.repository;

import cesde.integrador.entity.Prioridad;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface PrioridadRepository extends JpaRepository<Prioridad, UUID> {

    Optional<Prioridad> findByNivel(Short nivel);
}
