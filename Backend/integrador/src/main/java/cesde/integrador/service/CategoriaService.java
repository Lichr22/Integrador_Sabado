package cesde.integrador.service;

import cesde.integrador.dto.CategoriaDto;
import java.util.List;
import java.util.UUID;

public interface CategoriaService {

    List<CategoriaDto> getAll();

    CategoriaDto getById(UUID id);

    CategoriaDto create(CategoriaDto dto);

    CategoriaDto update(UUID id, CategoriaDto dto);

    void delete(UUID id);
}
