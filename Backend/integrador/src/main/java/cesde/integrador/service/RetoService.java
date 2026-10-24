package cesde.integrador.service;

import cesde.integrador.dto.RetoDto;
import java.util.List;
import java.util.UUID;

public interface RetoService {

    List<RetoDto> getAll();

    RetoDto getById(UUID id);

    RetoDto create(RetoDto dto);

    RetoDto update(UUID id, RetoDto dto);

    void delete(UUID id);
}
