package cesde.integrador.mapper;

import cesde.integrador.dto.RetoDto;
import cesde.integrador.entity.Reto;
import java.util.List;
import org.mapstruct.Mapper;
import org.mapstruct.Mapping;

@Mapper(componentModel = "spring")
public interface RetoMapper {

    @Mapping(source = "empresa.id", target = "empresaId")
    @Mapping(source = "empresa.nombre", target = "empresaNombre")
    @Mapping(source = "categoria.id", target = "categoriaId")
    @Mapping(source = "categoria.nombre", target = "categoriaNombre")
    @Mapping(source = "prioridad.id", target = "prioridadId")
    @Mapping(source = "prioridad.nombre", target = "prioridadNombre")
    RetoDto toDto(Reto entity);

    @Mapping(target = "empresa", ignore = true)
    @Mapping(target = "categoria", ignore = true)
    @Mapping(target = "prioridad", ignore = true)
    Reto toEntity(RetoDto dto);

    List<RetoDto> toDtoList(List<Reto> entities);
}
