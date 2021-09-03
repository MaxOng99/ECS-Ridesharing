from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog
from os.path import expanduser
from ui.ui_data import ui_data


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()

        # Load UI Widgets
        uic.loadUi('src/ui/config_interface.ui', self)
        self.widgets = self.create_widget_reference()
        self.populate_ui_data()
        self.set_widget_signals()
        self.set_initial_ui_state()

        # Applying Stylings
        with open("src/ui/style.qss","r") as fh:
            self.setStyleSheet(fh.read())

        self.selected_path = ""

    def set_initial_ui_state(self):
        spinboxes = self.findChildren(QtWidgets.QSpinBox)
        double_spinboxes = self.findChildren(QtWidgets.QDoubleSpinBox)

        maximum = 100000
        minimum = -100000
        for spinbox in spinboxes:
            if "Mean" in spinbox.objectName() or \
                "Std" in spinbox.objectName():
                    spinbox.setMaximum(maximum)
                    spinbox.setMinimum(minimum)
            else:
                spinbox.setMaximum(maximum)
        for double_spinbox in double_spinboxes:
            if "Mean" in double_spinbox.objectName() or \
                "Std" in double_spinbox.objectName():
                double_spinbox.setMaximum(maximum)
                double_spinbox.setMinimum(minimum)
            else:
                double_spinbox.setMaximum(maximum)

        self.widgets["graph"]["clusters"].setValue(5)
        self.widgets["graph"]["inter_dist"]["distribution"].setCurrentText("normal")
        self.widgets["graph"]["intra_dist"]["distribution"].setCurrentText("normal")
        self.widgets["optimiser"]["algorithm"].setCurrentText("greedy insert")

    def create_widget_reference(self):
        widgets = dict()

        widgets["passenger"] = {
            "num_passengers": self.numberOfPassengersSpinBox
        }

        widgets["graph"] = {
            "locations": self.locationsSpinBox,
            "clusters": self.clustersSpinBox,
            "cluster_radius": self.clusterRadiusDoubleSpinBox,
            "max_area": self.maximumAreaDoubleSpinBox,
            "inter_dist": {
                "distribution": self.interClusterDistributionComboBox,
                "normal":{
                    "mean": self.interMeanDoubleSpinBox,
                    "std": self.interStdDoubleSpinBox,
                    "mean_label": self.interMeanLabel,
                    "std_label": self.interStdLabel
                }
            },
            "intra_dist": {
                "distribution": self.intraClusterDistributionComboBox,
                "normal": {
                    "mean": self.intraMeanDoubleSpinBox,
                    "std": self.intraStdDoubleSpinBox,
                    "mean_label": self.intraMeanLabel,
                    "std_label": self.intraStdLabel
                }
            }
        }

        widgets["bus_service"] = {
            "avg_vehicle_speed": self.avgSpeedDoubleSpinBox,
            "service_hours": self.serviceHoursSpinBox
        }

        widgets["optimiser"] = {
            "objective": self.objectiveComboBox,
            "algorithm": self.algorithmComboBox,
            "greedy_params": {
                "iterations": self.iterationsSpinBox,
                "final_voting_rule": self.finalVotingRuleComboBox,
                "iterationsLabel": self.iterationsLabel,
                "final_voting_rule_label": self.finalVotingRuleLabel
            },
            "iterative_params": {
                "final_voting_rule": self.finalVotingRuleComboBox,
                "iterative_voting_rule": self.iterativeVotingRuleComboBox,
                "final_voting_rule_label": self.finalVotingRuleLabel,
                "iterative_voting_rule_label": self.iterativeVotingRuleLabel
            }
        }

        widgets["experiment"] = {
            "num_runs": self.numberOfRunsSpinBox,
            "output_directory": self.browsePushButton,
            "filename": self.filenameLineEdit,
            "output_path": self.outputPathLabel,
            "run": self.runPushButton
        }

        return widgets
    def populate_ui_data(self):

        # Graph
        self.widgets["graph"]["inter_dist"]["distribution"]\
            .addItems(ui_data["graph"]["inter_cluster_distributions"])
        self.widgets["graph"]["intra_dist"]["distribution"]\
            .addItems(ui_data["graph"]["intra_cluster_distributions"])

        # Optimiser
        self.widgets["optimiser"]["objective"]\
            .addItems(ui_data["optimiser"]["objectives"])
        
        self.widgets["optimiser"]["algorithm"]\
            .addItems(ui_data["optimiser"]["algorithms"])
        
        self.widgets["optimiser"]["iterative_params"]["iterative_voting_rule"]\
            .addItems(ui_data["optimiser"]["iterative_params"]["iterative_voting_rules"])
        
        self.widgets["optimiser"]["iterative_params"]["final_voting_rule"]\
            .addItems(ui_data["optimiser"]["iterative_params"]["final_voting_rules"])

    def set_widget_signals(self):
        # Graph Section
        self.widgets["graph"]\
            ["clusters"].valueChanged\
                .connect(self.__change_cluster_display)
        
        self.widgets["graph"]["inter_dist"]["distribution"]\
            .currentTextChanged.connect(lambda: self.__change_distribution_display(self.widgets["graph"]["inter_dist"]))
        
        self.widgets["graph"]["intra_dist"]["distribution"]\
            .currentTextChanged.connect(lambda: self.__change_distribution_display(self.widgets["graph"]["intra_dist"]))
        
        # Optimiser Section
        self.widgets["optimiser"]["algorithm"]\
            .currentTextChanged.connect(self.__change_algo_params_display)

        # Experiment Section
        self.widgets["experiment"]["output_directory"].clicked\
            .connect(self.__browse_output_path)
        self.widgets["experiment"]["filename"].textChanged.connect(self.__edit_output_path)

        self.widgets["experiment"]["run"].clicked.connect(self.__call_simulation_script)

    def __call_simulation_script(self):
        pass

    def __change_distribution_display(self, widget_group):
        selected_distribution = widget_group["distribution"].currentText()

        if selected_distribution == "uniform":
            for key, widget in widget_group["normal"].items():
                widget.hide()
        else:
            for _, widget in widget_group["normal"].items():
                widget.show()

    def __change_algo_params_display(self):
        selected_algorithm = self.widgets["optimiser"]["algorithm"].currentText()
        greedy_params_widgets = self.widgets["optimiser"]["greedy_params"]
        iterative_params_widgets = self.widgets["optimiser"]["iterative_params"]

        if selected_algorithm == "greedy insert":            
            for _, widget in iterative_params_widgets.items():
                widget.hide()
            
            for _, widget in greedy_params_widgets.items():
                widget.show()

        else:
            for _, widget in greedy_params_widgets.items():
                widget.hide()

            for _, widget in iterative_params_widgets.items():
                widget.show()
    
    def __change_cluster_display(self):
        if self.clustersSpinBox.value() > 1:
            self.interClusterGroupBox.setEnabled(True)
            self.intraClusterGroupBox.setEnabled(True)
        
        else:
            self.interClusterGroupBox.setEnabled(False)
            self.intraClusterGroupBox.setEnabled(False)

    def __browse_output_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory", expanduser("~"))
        self.widgets["experiment"]["output_path"].setText(f"{path}/{self.widgets['experiment']['filename'].text()}")
        self.selected_path = path
        
        self.widgets["experiment"]["filename"].setEnabled(True)

    def __edit_output_path(self):
        full_file_path = f"{self.selected_path}/{self.filenameLineEdit.text()}"
        self.widgets["experiment"]["output_path"].setText(full_file_path)