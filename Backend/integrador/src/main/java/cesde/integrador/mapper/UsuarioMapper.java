package cesde.integrador.mapper;

import cesde.integrador.dto.UsuarioDto;
import cesde.integrador.entity.Usuario;
import java.util.List;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

@Mapper(componentModel = "spring")
public interface UsuarioMapper {

    @Mapping(target = "contrasena", ignore = true)
    UsuarioDto toDto(Usuario entity);

    @Mapping(target = "contrasenaHash", ignore = true)
    Usuario toEntity(UsuarioDto dto);

    List<UsuarioDto> toDtoList(List<Usuario> entities);
}
