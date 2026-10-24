package cesde.integrador.service;

import cesde.integrador.dto.UsuarioDto;
import java.util.List;
import java.util.UUID;

public interface UsuarioService {

    List<UsuarioDto> getAll();

    UsuarioDto getById(UUID id);

    UsuarioDto create(UsuarioDto dto);

    UsuarioDto update(UUID id, UsuarioDto dto);

    void delete(UUID id);
}
