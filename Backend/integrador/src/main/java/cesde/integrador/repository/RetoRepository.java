package cesde.integrador.repository;

import cesde.integrador.entity.Reto;
import java.util.List;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface RetoRepository extends JpaRepository<Reto, UUID> {

    List<Reto> findByEmpresaId(UUID empresaId);

    List<Reto> findByCategoriaId(UUID categoriaId);

    List<Reto> findByEstado(String estado);
}
