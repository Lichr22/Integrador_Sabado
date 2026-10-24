package cesde.integrador.mapper;

import cesde.integrador.dto.RegistroDto;
import cesde.integrador.entity.Registro;
import java.util.List;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

@Mapper(componentModel = "spring")
public interface RegistroMapper {

    @Mapping(source = "usuario.id", target = "usuarioId")
    @Mapping(source = "usuario.nombre", target = "usuarioNombre")
    @Mapping(source = "reto.id", target = "retoId")
    @Mapping(source = "reto.nombre", target = "retoNombre")
    RegistroDto toDto(Registro entity);

    @Mapping(target = "usuario", ignore = true)
    @Mapping(target = "reto", ignore = true)
    Registro toEntity(RegistroDto dto);

    List<RegistroDto> toDtoList(List<Registro> entities);
}
