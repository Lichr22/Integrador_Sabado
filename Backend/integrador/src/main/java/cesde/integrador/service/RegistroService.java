package cesde.integrador.service;

import cesde.integrador.dto.RegistroDto;
import java.util.List;
import java.util.UUID;

public interface RegistroService {

    List<RegistroDto> getAll();

    RegistroDto getById(UUID id);

    RegistroDto create(RegistroDto dto);

    RegistroDto update(UUID id, RegistroDto dto);

    void delete(UUID id);
}
