// Javascript pour l'expérience analogique/analogique

$(function(){
    // positionne les paramètres 1 et 2 à deux valeurs différentes
    if ($("#id_param1").val()==$("#id_param2").val()){
	$("#id_param1").val("0");
	$("#id_param2").val("1");
    }
    getRangeFromParameter(1,$("#id_param1").val());
    getRangeFromParameter(2,$("#id_param2").val());
    $("#id_param1").on('change', function(){
	return function(){
	    getRangeFromParameter(1,$("#id_param1").val());
	}
    }());
    $("#id_param2").on('change', function(){
	return function(){
	    getRangeFromParameter(2,$("#id_param2").val());
	}
    }());
})

/**
 * récupération de l'intervalle correct pour le paramètre numéro n
 * @param which lequel des paramètres (paramètre 1 ou 2)
 * @param n numéro du paramètre
 * place les valeurs disponibles dans le widget FilteredSelect
 * qui correspond au paramètre.
 */
function getRangeFromParameter(which, n){
    var jqxhr = $.get("/plans/intervalles",{analog_data: n})
	.done(function(data){
	    // data contient les champs param, min, max et ok
	    var formfield=$("div.field-val"+which).first();
	    var text=data.param+". Il faut exactement choisir ";
	    var nb="3 valeurs";
	    if (which==2) nb="4 valeurs";
	    text+=nb+" :";
	    formfield.find("label").first().text(text);
	    var select=formfield.find("select").first();
	    // supprime les choix préexistants
	    select.find("option").remove();
	    // place les choix possibles
	    for(var i=parseInt(data.min); i<=parseInt(data.max); i++){
		select.append($("<option>",{value:i}).text(i));
	    }
	    // change le comportement du widget
	    select.select2({placeholder: nb});
	    $("span.select2-container").css({width: "15em",});
	    $("input.select2-search__field").css({width: "13em",});
	});
}
