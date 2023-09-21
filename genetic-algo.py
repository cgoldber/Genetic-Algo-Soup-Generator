import numpy as np
import random
import os

class Ingredient ():
    def __init__(self, name, amount):
        self.name = name
        self.amount = amount
    
    def set_amount(self, amount):
        """ Sets the amount of the ingredient in oz.
        """
        self.amount = amount

    def get_amount(self):
        """ Returns the amount of the ingredient in oz.
        """
        return self.amount
    
    def get_name(self):
        """ Returns the name of the ingredient.
        """
        return self.name

    def set_name(self, name):
        """ Sets the name of the ingredient.
        """
        self.name = name
    
    def __str__(self):
        """ Returns a string representation of the ingredient.
        """
        return str(round(self.amount, 2)) + " oz " + self.name


class Recipe():
    def __init__(self, num_new_recipes, recipe_strs):
        self.name = "recipe_" + str(num_new_recipes)
        self.ingredients = []
        self.make_ingredient_objects(recipe_strs=recipe_strs)
    
    
    def make_ingredient_objects(self, recipe_strs):
        """Reads recipe_strs and populates self.ingredients with ingredient objects.
           Args:
                recipe_strs (list) : list of the strings corresponding to ingredient/amt in the recipe
        """
        #makes dictionary mapping ingredients to the corresponding amounts
        recipe_dic = {}
        for line in recipe_strs: 
            information = line.split(" oz ")
            amt = float(information[0])
            name = information[1]
            if name not in recipe_dic.keys():
                recipe_dic[name] = amt
            else:
                curr_amt = recipe_dic[name]
                recipe_dic[name] = curr_amt + amt
        
        #populates self.ingredients with ingredient objects
        for ingr, ingr_amt in recipe_dic.items():
            self.ingredients.append(Ingredient(ingr, ingr_amt))

    def change_amount(self):
        """An ingredient is selected uniformly at random from the recipe.  
        Its quantity is set to a new value somehow (up to you).
        """
        ingredient = np.random.choice(self.ingredients)
        # remove or add up to 100% of original amount 
        new_amt = (random.uniform(-.9,.9) + 1) * ingredient.get_amount()
        ingredient.set_amount(new_amt)

    def add_ingredient(self, all_ingredients):
        """An ingredient is selected uniformly at random from the inspiring set and added to the recipe. 
        The amount of the new ingredient is determined randomly as a random number between 0 and 100 oz.
        Args:
            all_ingredients (set) : A set containing all unique possible ingredients
        """
        curr_ingredient_strs = [ingr.get_name() for ingr in self.ingredients]
        new_possible_ingredients = all_ingredients.difference(curr_ingredient_strs)

        if len(new_possible_ingredients) == 0: #skip if no new ingredients to add
            return

        new_ingredient = random.choice(tuple(new_possible_ingredients))

        new_name = random.choice(tuple(all_ingredients))
        # choose a random amount between 0 and 100 oz 
        new_amt = np.random.choice(range(0,100))
        new_ingredient = Ingredient(new_name, new_amt)
        self.ingredients.append(new_ingredient)

    def delete_ingredient(self):
        """An ingredient is selected uniformly at random from the recipe and removed from the recipe.
        """
        selected_ing = random.choice(self.ingredients)
        self.ingredients.remove(selected_ing)

    def swap_ingredient(self, all_ingredients):
        """An ingredient is selected uniformly at random from the recipe. Its name attribute 
        is changed to that of another ingredient that is chosen at random from the ones 
        stored in the inspiring set.
        Args:
            all_ingredients (set) : A set containing all unique possible ingredients
        """
        ingredient = random.choice(self.ingredients)
        choices = all_ingredients.difference({ingredient.get_name()})
        new_name = random.choice(tuple(choices))
        ingredient.set_name(new_name)
        return ingredient
    
    def combine_duplicate_ingredients(self): 
        # loop through all ingredients
        checked_ingredients = [self.ingredients[0].copy()]
        for ing in self.ingredients: 
            for checked_ing in checked_ingredients:
                if ing.get_name() == checked_ing.get_name(): 
                    checked_ing.set_amount(checked_ing.get_amount() + ing.get_amount())
                else: 
                    checked_ingredients.append(ing)
        self.ingredients = checked_ingredients
    
    def normalize(self):
        """Normalizes all ingredients so amount adds up to 100 oz.
        """
        current_total = 0
        for ingredient in self.ingredients: 
            current_total += ingredient.get_amount() 
        if current_total == 100: #already normalized
            return    
        sizing_factor = 100 / current_total
        for ingredient in self.ingredients: 
            new_amt = ingredient.get_amount() * sizing_factor
            if new_amt < .01: #delete ingredient if normalization makes it below .01 oz
                self.ingredients.remove(ingredient)
            else:
                ingredient.set_amount(new_amt)
        
    def get_fitness(self):
        """Returns fitness score
        """
        return len(self.ingredients)
    
    def get_ingredient_strings(self):
        """Returns the ingredients of the recipes as a list of strings
        """
        return [str(ingredient) for ingredient in self.ingredients]
    
    def get_ingredients(self):
        """Returns the ingredient list
        """
        return self.ingredients
    
    def get_name(self):
        """Returns the name of the recipe.
        """
        return self.name

    def mutate(self, all_ingredients):
        """Based on some set probability (40%), returns original recipe 60% of the time. Otherwise, 
        calls some mutation (change_amount, add_ingredient, delete_ingredient, or swap_ingredient) 
        with equal probability. Then calls normalize function.
        Args:
            all_ingredients (set) : A set containing all unique possible ingredients
        """
        mutate = np.random.choice([True, False], p=[0.4,0.6])
        if mutate: 
            mutation = np.random.randint(0,4)
            if mutation == 0: 
                self.change_amount() 
            elif mutation == 1: 
                self.add_ingredient(all_ingredients)
            elif mutation == 2: 
                self.delete_ingredient()
            elif mutation == 3: 
                self.swap_ingredient(all_ingredients)
            # normalize ingredient amounts after mutation 
            self.normalize()


class RecipeManager():
    def __init__(self):
        self.recipes = []
        self.num_new_recipes = 0
        self.all_ingredients = set() # inspiring set of unique ingredients 
    
    def parse_files(self):
        """ Read file of recipes and populates recipe list with recipe object,
        passing in a list representation of recipe.
        """
        print("Reading Initial Recipe Files")
        dir = "input"
        for file in os.listdir(dir):
            with open(dir + "/" + file, "r") as f:
                recipe_str = f.readlines()
                self.recipes.append(Recipe(self.num_new_recipes, recipe_str))
            self.num_new_recipes += 1

    def get_unique_ingredients(self):
        """ Iterates through all of the recipe objects and gets all of the unique ingredients.
        """
        for recipe in self.recipes:
            ingredients = recipe.get_ingredients()
            for ingredient in ingredients:
                self.all_ingredients.add(ingredient.get_name())
        print(f"There are {len(self.all_ingredients)} possible ingredients in the inspiring set")

    def crossover(self, recipe1, recipe2):
        """Chooses a random pivot index to concatenate the recipes. Creates a new recipe object. Then
        calls the mutate function on the new recipe and stores what's returned.
            Args:
                recipe1 (Recipe) : first recipe to be crossed
                recipe2 (Recipe) : second recipe to be crossed
        """
        #randomly select pivot
        shortest_recipe_len = min((recipe1.get_fitness()), (recipe2.get_fitness()))
        pivot = np.random.randint(0, shortest_recipe_len)

        #split the recipes based on the pivot and make a new recipe
        recipe1_strs = recipe1.get_ingredient_strings()
        recipe2_strs = recipe2.get_ingredient_strings()
        cross = recipe1_strs[:pivot] + recipe2_strs[pivot:]

        newRecipe = Recipe(self.num_new_recipes, cross)
        self.num_new_recipes += 1

        #call recipe to be potentially mutated
        newRecipe.mutate(self.all_ingredients)
        return newRecipe
    
    def fittest_half(self, recipes):
        """ Returns the fittest 50% of a given population.
            Args:
                recipes (list) : list of recipes
        """
        sorted_recipes = sorted(recipes, key = lambda x : x.get_fitness())
        return sorted_recipes[int(len(recipes)/2):]

    def genetic_algo(self):
        """ Iterate len(self.recipes) times. Choose recipe1 and recipe2 based on fitness probabilites
        and cross them over (making new recipe object). Then it's going to call the mutate function on
        it and stores all of the new recipes in new_recipes. At the end, it is going to taking the top
        50% of the new and old recipes and store it in self.recipes. 
        """
        new_recipes = []
        for _ in range(len(self.recipes)):
            #chooses two recipes based on probability corresponding to their fitness
            fitnesses = [recipe.get_fitness() for recipe in self.recipes]
            sum_fit = sum(fitnesses)
            p = [fit / sum_fit for fit in fitnesses]
            recipe1, recipe2 = np.random.choice(self.recipes, p = p, size = 2, replace = False)

            #cross the recipes together
            new_recipe = self.crossover(recipe1, recipe2)
            new_recipes.append(new_recipe)

        #keep top 50% of old recipes and newly generated recipes for next generation
        self.recipes = self.fittest_half(self.recipes) + self.fittest_half(new_recipes)   

    def run_genetic_algo(self, generations):
        """ Run genetic algorithm for the # of generations that the user inputs.
            Args:
                generations (int) : number of times the genetic algo will run
        """
        for i in range(generations):
            print(f"Running genetic algorithm for generation {i + 1}")
            self.genetic_algo()  
    
    def write_fittest_recipes(self):
        """ Writes the 5 fittest recipes to files in the fittest recipes folder.
        """
        sorted_recipes = sorted(self.recipes, key = lambda x : x.get_fitness())
        top_5 = sorted_recipes[-5:]
        for i in range(5):
            recipe = top_5[i]
            with open("fittest recipes/rank_" + str(5 - i), "w") as f:
                f.write(f"{recipe.get_name()} ({recipe.get_fitness()} ingredients)\n")
                f.writelines(recipe.get_ingredient_strings())


def main():
    generations = int(input("How many generations would you like to run this algorithm for? "))
    manager = RecipeManager()
    manager.parse_files()
    manager.get_unique_ingredients()
    manager.run_genetic_algo(generations)
    manager.write_fittest_recipes() #writes top 5 fittest recipes (after algo) to a file
    print("All done :)")


if __name__ == "__main__":
    main()
