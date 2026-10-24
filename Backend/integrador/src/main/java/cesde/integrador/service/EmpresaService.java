package cesde.integrador.service;

import cesde.integrador.dto.EmpresaDto;
import java.util.List;
import java.util.UUID;

public interface EmpresaService {

    List<EmpresaDto> getAll();

    EmpresaDto getById(UUID id);

    EmpresaDto create(EmpresaDto dto);

    EmpresaDto update(UUID id, EmpresaDto dto);

    void delete(UUID id);
}
