package cesde.integrador.mapper;

import cesde.integrador.dto.CategoriaDto;
import cesde.integrador.entity.Categoria;
import java.util.List;
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface CategoriaMapper {

    CategoriaDto toDto(Categoria entity);

    Categoria toEntity(CategoriaDto dto);

    List<CategoriaDto> toDtoList(List<Categoria> entities);
}
