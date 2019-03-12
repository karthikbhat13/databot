var app = angular.module('mainModule', []);
app.controller('mainController', ['$scope', '$http', function($scope, $http){
    $scope.obj = {
        send : function(){
            alert("SEND");
        }
    }
}]);