import newick
from typing import Dict, List, Union, Optional

from s_locus_finder_reporter.model.AnalysisConfiguration import AnalysisConfiguration
from s_locus_finder_reporter.model.FamilyAnalysis import FamilyAnalysis
from s_locus_finder_reporter.model.ModelAnalysis import ModelAnalysis
from s_locus_finder_reporter.model.RegionAnalysis import RegionAnalysis
from s_locus_finder_reporter.model.RegionModelAnalysis import RegionModelAnalysis
from s_locus_finder_reporter.model.RegionTreeDistance import RegionTreeDistance
from s_locus_finder_reporter.model.SLFDatabase import SLFDatabase
from s_locus_finder_reporter.model.SpeciesAnalysis import SpeciesAnalysis

RegionTreeDistanceDict = Dict[str, Union[str, float]]
RegionModelAnalysisDict = Dict[str, Union[List[RegionTreeDistanceDict], List[float], Optional[int], Optional[str]]]
ModelAnalysisDict = Dict[str, Union[str, Optional[RegionModelAnalysisDict]]]
RegionAnalysisDict = Dict[str, Union[str, Dict[str, ModelAnalysisDict]]]
SpeciesAnalysisDict = Dict[str, Union[str, Optional[int], Optional[str], Dict[str, RegionAnalysisDict]]]
FamilyAnalysisDict = Dict[str, Union[str, Dict[str, SpeciesAnalysisDict]]]

AnalysisConfigurationDict = Dict[str, Union[str, Dict[str, str]]]

SLFDatabaseInfoDict = Dict[str, str]
SLFDatabaseDict = Dict[
    str, Union[SLFDatabaseInfoDict, Dict[str, AnalysisConfigurationDict], Dict[str, FamilyAnalysisDict]]
]


class SLFDatabaseMapper:
    def __init__(self, database: SLFDatabase):
        self.__database: SLFDatabase = database

    def get_database(self) -> SLFDatabaseDict:
        return {
            'info': {
                'name': self.__database.database_name,
                'description': self.__database.description,
            },
            'newick': newick.dumps(self.__database.newick),
            'configurations': {
                configuration.configuration_name: SLFDatabaseMapper.__map_configuration(configuration)
                for configuration
                in self.__database.configurations
            },
            'families': {
                family.family_name: SLFDatabaseMapper.__map_family(family)
                for family
                in self.__database.family_analysis
            }
        }

    @staticmethod
    def __map_configuration(configuration: AnalysisConfiguration) -> AnalysisConfigurationDict:
        return {
            'name': configuration.configuration_name,
            'version': configuration.version,
            'parameters': configuration.parameters
        }

    @staticmethod
    def __map_family(family: FamilyAnalysis):
        return {
            'name': family.family_name,
            'speciesAnalysis': {
                species_analysis.species_name: SLFDatabaseMapper.__map_species_analysis(species_analysis)
                for species_analysis in family.species_analysis.species_analysis
            }
        }

    @staticmethod
    def __map_species_analysis(analysis: SpeciesAnalysis) -> SpeciesAnalysisDict:
        return {
            'name': analysis.species_name,
            'predictedSkp1': analysis.predicted_skp1,
            'putativeSkp1': analysis.putative_skp1,
            'predictedSkp1TreePath': analysis.predicted_skp1_tree_path,
            'putativeSkp1TreePath': analysis.putative_skp1_tree_path,
            'regionAnalysis': {
                region_analysis.region_name: SLFDatabaseMapper.__map_region_analysis(region_analysis)
                for region_analysis in analysis.region_analysis
            }
        }

    @staticmethod
    def __map_region_analysis(analysis: RegionAnalysis) -> RegionAnalysisDict:
        return {
            'name': analysis.region_name,
            'modelAnalysis': {
                model_analysis.model_name: SLFDatabaseMapper.__map_model_analysis(model_analysis)
                for model_analysis in analysis.model_analysis
            }
        }

    @staticmethod
    def __map_model_analysis(model_analysis: ModelAnalysis) -> ModelAnalysisDict:
        return {
            'name': model_analysis.model_name,
            'predicted': SLFDatabaseMapper.__map_region_model_analysis(model_analysis.predicted)
            if model_analysis.predicted is not None else None,
            'putative': SLFDatabaseMapper.__map_region_model_analysis(model_analysis.putative)
            if model_analysis.putative is not None else None
        }

    @staticmethod
    def __map_region_model_analysis(model: RegionModelAnalysis) -> RegionModelAnalysisDict:
        return {
            'minTreeDistances': [
                SLFDatabaseMapper.__map_min_tree_distance(min_tree_distance)
                for min_tree_distance in model.min_tree_distances
            ],
            'isoelectricPoints': list(model.isoelectric_points),
            'genesInRegion': model.genes_in_region,
            'modelFastaPath': model.model_fasta_path,
            'regionPdfPath': model.region_pdf_path,
            'phylogenyTreePath': model.phylogeny_tree_path
        }

    @staticmethod
    def __map_min_tree_distance(tree_distance: RegionTreeDistance) -> RegionTreeDistanceDict:
        return {
            'region': tree_distance.region,
            'regionSequence': tree_distance.region_sequence,
            'positiveBestSequence': tree_distance.positive_best_sequence,
            'positiveMin': tree_distance.positive_min,
            'negativeBestSequence': tree_distance.negative_best_sequence,
            'negativeMin': tree_distance.negative_min,
            'score': tree_distance.score
        }
