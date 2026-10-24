package cesde.integrador.repository;

import cesde.integrador.entity.Registro;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface RegistroRepository extends JpaRepository<Registro, UUID> {

    List<Registro> findByUsuarioId(UUID usuarioId);

    List<Registro> findByRetoId(UUID retoId);

    boolean existsByUsuarioIdAndRetoId(UUID usuarioId, UUID retoId);
}
