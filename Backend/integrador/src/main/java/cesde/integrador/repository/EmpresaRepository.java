package cesde.integrador.repository;

import cesde.integrador.entity.Empresa;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface EmpresaRepository extends JpaRepository<Empresa, UUID> {

    Optional<Empresa> findByNit(String nit);

    List<Empresa> findByActiva(Boolean activa);
}
