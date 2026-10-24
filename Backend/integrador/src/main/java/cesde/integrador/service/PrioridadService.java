package cesde.integrador.service;

import cesde.integrador.dto.PrioridadDto;
import java.util.List;
import java.util.UUID;

public interface PrioridadService {

    List<PrioridadDto> getAll();

    PrioridadDto getById(UUID id);

    PrioridadDto create(PrioridadDto dto);

    PrioridadDto update(UUID id, PrioridadDto dto);

    void delete(UUID id);
}
