package dk.itu.mario.engine.level;

import java.util.Random;
import java.util.*;

//Make any new member variables and functions you deem necessary.
//Make new constructors if necessary
//You must implement mutate() and crossover()


public class MyDNA extends DNA
{
	
	public int numGenes = 0; //number of genes

	// Return a new DNA that differs from this one in a small way.
	// Do not change this DNA by side effect; copy it, change the copy, and return the copy.
	public MyDNA mutate ()
	{
		MyDNA copy = new MyDNA();
		//YOUR CODE GOES BELOW HERE
		// Get a random index that will be mutated
		Random random = new Random();
		int randIndex = random.nextInt(this.chromosome.length());
		// Get a random capital char that used to replace the old one
		char newChar = (char) ('A' + random.nextInt(26));
		// System.out.println("hahahah:"+newChar);
		// Create a new chromosome to store the mutated chromosome
		String newChromo = "";
		// create the new chromosome by replacing with the new character
		for (int i = 0; i < this.chromosome.length(); i++){
			
			if (i == randIndex){
				newChromo = newChromo + newChar;
			}else{
				newChromo = newChromo + this.chromosome.charAt(i);
			}
		}
		// System.out.println("dna:"+this.chromosome);
		// System.out.println("newdna:"+newChromo);
		copy.setChromosome(newChromo);
		//copy.setLength(newChromo.length());
		//YOUR CODE GOES ABOVE HERE
		return copy;
	}
	
	// Do not change this DNA by side effect
	public ArrayList<MyDNA> crossover (MyDNA mate)
	{
		ArrayList<MyDNA> offspring = new ArrayList<MyDNA>();
		//YOUR CODE GOES BELOW HERE
		// Get random index to cut the chromosome
		Random random = new Random();
		int crossoverIdx = random.nextInt(this.chromosome.length());
		// cut off and rebuild the chromosome
		String child1_chromo = this.chromosome.substring(0, crossoverIdx) + mate.chromosome.substring(crossoverIdx);
		String child2_chromo = mate.chromosome.substring(0, crossoverIdx) + this.chromosome.substring(crossoverIdx);
		// Create new DNA and assign the new chromosome to them
		MyDNA offspring1 = new MyDNA();
		MyDNA offspring2 = new MyDNA();
		offspring1.setChromosome(child1_chromo);
		offspring2.setChromosome(child2_chromo);
		// Add to the return list
		offspring.add(offspring1);
		offspring.add(offspring2);
		//YOUR CODE GOES ABOVE HERE
		return offspring;
	}
	
	// Optional, modify this function if you use a means of calculating fitness other than using the fitness member variable.
	// Return 0 if this object has the same fitness as other.
	// Return -1 if this object has lower fitness than other.
	// Return +1 if this objet has greater fitness than other.
	public int compareTo(MyDNA other)
	{
		int result = super.compareTo(other);
		//YOUR CODE GOES BELOW HERE
		if(this.getFitness() > other.getFitness()){
			return +1;
		}else if(this.getFitness() == other.getFitness()){
			return 0;
		}else{
			return 1;
		}
		//YOUR CODE GOES ABOVE HERE
		//return result;
	}
	
	
	// For debugging purposes (optional)
	public String toString ()
	{
		String s = super.toString();
		//YOUR CODE GOES BELOW HERE
		
		//YOUR CODE GOES ABOVE HERE
		return s;
	}
	
	public void setNumGenes (int n)
	{
		this.numGenes = n;
	}

}

