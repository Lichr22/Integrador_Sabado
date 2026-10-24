package cesde.integrador.mapper;

import cesde.integrador.dto.PrioridadDto;
import cesde.integrador.entity.Prioridad;
import java.util.List;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface PrioridadMapper {

    PrioridadDto toDto(Prioridad entity);

    Prioridad toEntity(PrioridadDto dto);

    List<PrioridadDto> toDtoList(List<Prioridad> entities);
}
